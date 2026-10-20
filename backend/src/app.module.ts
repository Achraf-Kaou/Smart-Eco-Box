import { Logger, Module, OnModuleInit } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import databaseConfig from './config/database.config';
import { InjectConnection, MongooseModule } from '@nestjs/mongoose';
import { Connection } from 'mongoose';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [databaseConfig],
    }),
    MongooseModule.forRootAsync({
    imports: [ConfigModule],
    useFactory: async (configService: ConfigService) => ({
      uri: configService.get<string>('database.uri'),
    }),
    inject: [ConfigService],
  }),
  ],
  controllers: [],
  providers: [],
})
export class AppModule implements OnModuleInit {
  private readonly logger = new Logger('DatabaseConnection');

  // Inject the underlying Mongoose connection object
  constructor(@InjectConnection() private readonly connection: Connection) {}

  onModuleInit() {
    // 1. Check immediate status on startup
    if (this.connection.readyState === 1) {
      this.logger.log('🚀 Successfully connected to MongoDB!');
    }

    // 2. Listen to ongoing lifecycle events
    this.connection.on('connected', () => {
      this.logger.log('🚀 MongoDB connection established.');
    });

    this.connection.on('error', (error) => {
      this.logger.error(`❌ MongoDB connection error: ${error.message}`);
    });

    this.connection.on('disconnected', () => {
      this.logger.warn('⚠️ MongoDB disconnected.');
    });
  }
}
