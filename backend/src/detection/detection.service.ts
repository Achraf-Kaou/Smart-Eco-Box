import { Injectable, Logger } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Detection, DetectionDocument } from './detection.schema';

@Injectable()
export class DetectionService {
  private readonly logger = new Logger(DetectionService.name);

  constructor(
    @InjectModel(Detection.name)
    private detectionModel: Model<DetectionDocument>,
  ) {}

  async saveDetection(data: any): Promise<Detection> {
    try {
      const detection = new this.detectionModel({
        event_id: data.event_id,
        user_id: data.user_id,
        user_name: data.user_name,
        waste_type: data.waste_type,
        confidence: data.confidence,
        original_class: data.original_class || '',
        points: data.points || 0,
        timestamp: data.timestamp,
      });

      const saved = await detection.save();
      this.logger.log(`Detection saved → user: ${saved.user_name} | +${saved.points} points`);
      return saved;
    } catch (error) {
      this.logger.error('Failed to save detection', error);
      throw error;
    }
  }

  // Optional: get total score of a user
  async getUserScore(userId: string): Promise<number> {
    const result = await this.detectionModel.aggregate([
      { $match: { user_id: userId } },
      { $group: { _id: '$user_id', totalPoints: { $sum: '$points' } } },
    ]);

    return result.length > 0 ? result[0].totalPoints : 0;
  }

  // Récupérer les dernières détections
async getRecentDetections(limit = 20) {
  return this.detectionModel
    .find()
    .sort({ createdAt: -1 })
    .limit(limit)
    .exec();
}

// Leaderboard (classement par points)
async getLeaderboard() {
  return this.detectionModel.aggregate([
    {
      $group: {
        _id: '$user_id',
        user_name: { $first: '$user_name' },
        totalPoints: { $sum: '$points' },
        totalDetections: { $sum: 1 },
      },
    },
    { $sort: { totalPoints: -1 } },
    { $limit: 10 },
  ]);
}
}