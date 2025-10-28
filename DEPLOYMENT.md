# Deploy RAG Chat Assistant to Vercel

This guide will help you deploy your beautiful RAG Chat Assistant to Vercel for free hosting.

## Prerequisites

1. **GitHub Account**: You'll need a GitHub account
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Anthropic API Key**: Your existing API key

## Step 1: Prepare Your Repository

1. **Create a GitHub Repository**:
   - Go to GitHub and create a new repository
   - Name it `rag-chat-assistant` (or any name you prefer)
   - Make it public or private (your choice)

2. **Upload Your Files**:
   - Upload all the files from your local project to the GitHub repository
   - Make sure to include:
     - `app.py`
     - `requirements.txt`
     - `vercel.json`
     - `templates/index.html`
     - `README.md`

## Step 2: Deploy to Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Environment Variables**:
   - In the Vercel dashboard, go to your project settings
   - Navigate to "Environment Variables"
   - Add these variables:
     ```
     ANTHROPIC_API_KEY = your_anthropic_api_key_here
     FLASK_SECRET_KEY = your-random-secret-key-here
     ```

3. **Deploy**:
   - Click "Deploy"
   - Wait for the deployment to complete (usually 2-3 minutes)

## Step 3: Access Your Application

Once deployed, Vercel will provide you with a URL like:
`https://your-project-name.vercel.app`

## Features After Deployment

✅ **Free Hosting**: Vercel provides free hosting for personal projects
✅ **Global CDN**: Fast loading worldwide
✅ **Automatic HTTPS**: Secure connections
✅ **Auto-deployment**: Updates automatically when you push to GitHub
✅ **Serverless**: Scales automatically based on usage

## Cost Benefits

- **Vercel**: Free tier includes 100GB bandwidth/month
- **Claude API**: Only pay for actual usage (your $5 will last much longer)
- **No Server Costs**: No need to maintain your own server

## Important Notes

⚠️ **Memory Limitations**: Vercel functions have memory limits, so very large documents might not work
⚠️ **Cold Starts**: First request might be slower due to serverless cold starts
⚠️ **File Storage**: Documents are processed in memory and not persisted between requests

## Troubleshooting

If you encounter issues:

1. **Check Environment Variables**: Make sure your API key is correctly set
2. **Check Logs**: Vercel provides detailed logs in the dashboard
3. **Function Timeout**: Increase timeout in `vercel.json` if needed
4. **Memory Issues**: Try smaller documents or optimize the code

## Updating Your Application

To update your application:
1. Make changes to your local files
2. Push changes to GitHub
3. Vercel automatically redeploys

## Support

- Vercel Documentation: [vercel.com/docs](https://vercel.com/docs)
- Anthropic API Docs: [docs.anthropic.com](https://docs.anthropic.com)

Your beautiful RAG Chat Assistant will be live and accessible from anywhere in the world! 🌍
