import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { getConnectionToken } from 'node_modules/@nestjs/mongoose/dist/common/mongoose.utils';
import { Connection } from 'mongoose';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const mongooseConnection = app.get<Connection>(getConnectionToken());
  
  if (mongooseConnection.readyState === 1) {
    console.log('Database verified from main.ts');
  }

  app.enableCors({
    origin: 'http://localhost:5173', // Vite default port
    credentials: true,
  });
  
  await app.listen(process.env.PORT ?? 4020);
}
bootstrap();
