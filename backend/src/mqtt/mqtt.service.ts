import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import * as mqtt from 'mqtt';
import { DetectionService } from '../detection/detection.service';

@Injectable()
export class MqttService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(MqttService.name);
  private client: mqtt.MqttClient;

  private readonly brokerUrl = 'mqtt://broker.emqx.io:1883';
  private readonly topic = 'smart/waste/detection';

  constructor(private readonly detectionService: DetectionService) {}

  onModuleInit() {
    this.connect();
  }

  private connect() {
    this.logger.log(`Connecting to MQTT broker: ${this.brokerUrl}`);

    this.client = mqtt.connect(this.brokerUrl, {
      clientId: `smart-eco-box-backend-${Math.random().toString(16).slice(2, 8)}`,
      clean: true,
      connectTimeout: 4000,
      reconnectPeriod: 1000,
    });

    this.client.on('connect', () => {
      this.logger.log('Connected to MQTT broker');
      this.client.subscribe(this.topic, (err) => {
        if (err) {
          this.logger.error(`Failed to subscribe to ${this.topic}`, err);
        } else {
          this.logger.log(`Subscribed to topic: ${this.topic}`);
        }
      });
    });

    this.client.on('message', async (topic, payload) => {
      try {
        const message = JSON.parse(payload.toString());
        this.logger.log(`Received message on ${topic}`);

        // 1. Sauvegarder en base
        const saved = await this.detectionService.saveDetection(message);

        // 2. Préparer et envoyer le feedback
        const feedback = {
          action: 'validate',
          event_id: saved.event_id,
          user_id: saved.user_id,
          user_name: saved.user_name,
          waste_type: saved.waste_type,
          points: saved.points,
          message: `Bravo ${saved.user_name} ! +${saved.points} points`,
          timestamp: new Date().toISOString(),
        };

        this.client.publish(
          'smart/waste/command',
          JSON.stringify(feedback),
          { qos: 1 },
          (err) => {
            if (err) {
              this.logger.error('Failed to publish feedback', err);
            } else {
              this.logger.log(`Feedback sent → ${feedback.message}`);
            }
          },
        );
      } catch (error) {
        this.logger.error('Failed to process message', error);
      }
    });

    this.client.on('error', (err) => {
      this.logger.error('MQTT error', err);
    });

    this.client.on('close', () => {
      this.logger.warn('MQTT connection closed');
    });
  }

  onModuleDestroy() {
    if (this.client) {
      this.client.end();
      this.logger.log('MQTT client disconnected');
    }
  }
}