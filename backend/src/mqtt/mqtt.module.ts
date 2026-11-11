import { Module } from '@nestjs/common';
import { MqttService } from './mqtt.service';
import { DetectionModule } from '../detection/detection.module';

@Module({
  imports: [DetectionModule],
  providers: [MqttService],
  exports: [MqttService],
})
export class MqttModule {}