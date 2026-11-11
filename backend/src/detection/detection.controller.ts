import { Controller, Get, Query } from '@nestjs/common';
import { DetectionService } from './detection.service';

@Controller('detections')
export class DetectionController {
  constructor(private readonly detectionService: DetectionService) {}

  @Get('recent')
  getRecent(@Query('limit') limit?: string) {
    return this.detectionService.getRecentDetections(
      limit ? parseInt(limit) : 20,
    );
  }

  @Get('leaderboard')
  getLeaderboard() {
    return this.detectionService.getLeaderboard();
  }
}