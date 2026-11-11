import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { Detection, DetectionSchema } from './detection.schema';
import { DetectionService } from './detection.service';
import { DetectionController } from './detection.controller';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: Detection.name, schema: DetectionSchema },
    ]),
  ],
  controllers: [DetectionController],
  providers: [DetectionService],
  exports: [DetectionService],
})
export class DetectionModule {}