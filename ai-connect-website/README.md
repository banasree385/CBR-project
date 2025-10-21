# AI Connect Website

A modern, responsive website for AI Connect project with integrated chatbot functionality.

## Project Structure

```
ai-connect-website/
├── frontend/
│   ├── index.html          # Homepage
│   ├── about.html          # About page
│   ├── contact.html        # Contact page
│   ├── blog.html           # Blog page
│   ├── chatbot.html        # Dedicated chatbot page
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── js/
│   │   ├── main.js         # Main JavaScript functionality
│   │   └── chatbot.js      # Chatbot widget functionality
│   └── images/             # Image assets
├── backend/
│   ├── server.js           # Express server
│   ├── routes/
│   │   ├── chatbot.js      # Chatbot API routes
│   │   └── contact.js      # Contact form routes
│   └── middleware/         # Custom middleware
├── package.json
├── .env.example           # Environment variables example
└── README.md
```

## Features

- 📱 **Responsive Design**: Optimized for mobile and desktop
- 🤖 **AI Chatbot**: Floating widget with OpenAI integration
- 🎨 **Modern UI**: Clean, light theme with intuitive navigation
- 📝 **Contact Form**: Functional contact form with email integration
- 📄 **Multi-page Site**: Homepage, About, Contact, Blog sections
- ⚡ **Fast Loading**: Optimized performance and lazy loading

## Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Responsive design with CSS Grid and Flexbox
- Modern CSS features (custom properties, animations)

**Backend:**
- Node.js with Express.js
- OpenAI API integration
- Email functionality with Nodemailer
- Security middleware (Helmet, CORS, Rate Limiting)

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ai-connect-website
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:3000`

## Environment Variables

Create a `.env` file in the root directory:

```env
PORT=3000
OPENAI_API_KEY=your_openai_api_key_here
EMAIL_SERVICE=gmail
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
NODE_ENV=development
```

## Deployment

### Azure Deployment

1. Create an Azure App Service
2. Configure environment variables in Azure
3. Deploy using Azure CLI or GitHub Actions
4. Detailed instructions in `docs/azure-deployment.md`

### AWS Deployment

1. Use AWS Elastic Beanstalk or EC2
2. Configure environment variables
3. Set up Load Balancer and SSL certificate
4. Detailed instructions in `docs/aws-deployment.md`

## API Endpoints

- `GET /` - Serve homepage
- `POST /api/chatbot/message` - Send message to chatbot
- `POST /api/contact` - Submit contact form
- `GET /api/health` - Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.