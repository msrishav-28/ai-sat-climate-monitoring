name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Streamlit Cloud
      env:
        STREAMLIT_DEPLOY_MESSAGE: ${{ github.event.head_commit.message }}
      run: |
        echo "Streamlit Cloud will auto-deploy from main branch"
        echo "Commit: $STREAMLIT_DEPLOY_MESSAGE"
    
    # Note: Streamlit Cloud automatically deploys when you push to main
    # No additional steps needed here

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Vercel CLI
      run: npm install --global vercel@latest
    
    - name: Pull Vercel Environment Information
      run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      working-directory: frontend
    
    - name: Build Project
      run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      working-directory: frontend
    
    - name: Deploy to Vercel
      run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
      working-directory: frontend