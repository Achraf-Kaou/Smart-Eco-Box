import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type DetectionDocument = Detection & Document;

@Schema({ timestamps: true })
export class Detection {
  @Prop({ required: true })
  event_id: string;

  @Prop({ required: true })
  user_id: string;

  @Prop({ required: true })
  user_name: string;

  @Prop({ required: true })
  waste_type: string;

  @Prop({ required: true })
  confidence: number;

  @Prop()
  original_class: string;

  @Prop({ required: true, default: 0 })
  points: number;

  @Prop()
  timestamp: string;
}

export const DetectionSchema = SchemaFactory.createForClass(Detection);