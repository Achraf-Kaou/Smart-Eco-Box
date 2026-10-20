import { registerAs } from '@nestjs/config'

export default registerAs('database', () => {
  const username = encodeURIComponent(process.env.MONGODB_USERNAME || '');
  const password = encodeURIComponent(process.env.MONGODB_PASSWORD || '');
  
  // Base URI part (e.g., @cluster0.example.mongodb.net/my_database)
  const baseUri = process.env.MONGODB_URI || 'localhost:27017/default_db';

  // Construct the full connection string dynamically
  const uri = username && password 
    ? `mongodb+srv://${username}:${password}@${baseUri}`
    : `mongodb://${baseUri}`;

  return { uri };
});