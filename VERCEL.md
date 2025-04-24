# Deploying PingCRM Backend to Vercel

This document explains how to deploy the PingCRM backend to Vercel's serverless platform.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. A PostgreSQL database (you can use [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres), [Supabase](https://supabase.com/), [Railway](https://railway.app/), or any other PostgreSQL provider)
3. The [Vercel CLI](https://vercel.com/docs/cli) installed locally: `npm i -g vercel`

## Steps for Deployment

### 1. Set up a PostgreSQL Database

You need to set up a PostgreSQL database since SQLite isn't suitable for serverless environments.

**Options:**
- Vercel Postgres
- Supabase
- Railway
- ElephantSQL
- Any other PostgreSQL provider

Make sure to get your database connection string. It should look like:
```
postgresql://username:password@host:port/database
```

### 2. Deploy using Vercel CLI

1. Navigate to your backend directory
   ```
   cd backend
   ```

2. Login to Vercel
   ```
   vercel login
   ```

3. Deploy the project
   ```
   vercel
   ```
   
   Follow the prompts to configure your project:
   - Set the framework to "Other"
   - Set the build command to empty
   - Set the output directory to `.`

4. Add environment variables in the Vercel dashboard:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `FRONTEND_URL`: The URL of your frontend app
   - `CORS_ORIGINS`: The URL of your frontend app (same as FRONTEND_URL)

### 3. Database Migration

Since you're now using PostgreSQL, you need to run Alembic migrations:

1. Update your local `.env` file with the PostgreSQL connection string
2. Run migrations:
   ```
   alembic upgrade head
   ```

### 4. Configure Frontend to Use Backend

Update your frontend app to point to your new backend URL:

1. In your frontend's `.env.production` file:
   ```
   VITE_API_URL=https://your-backend-app-name.vercel.app/api
   ```

2. Redeploy your frontend app

## Troubleshooting

- **Cold starts**: Serverless functions may experience a delay when they haven't been accessed for a while
- **Database connections**: Check that your DATABASE_URL is correct
- **CORS issues**: Make sure your CORS_ORIGINS and FRONTEND_URL variables are set correctly

## Limitations

- Vercel Functions are limited to 10 seconds of execution time
- Files uploaded to Vercel are read-only, so your app can't write to the filesystem
- Stateful applications may need to be redesigned for serverless 