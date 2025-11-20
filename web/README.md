# Parking Citation Appeal Assistant - Web Interface

A modern, user-friendly web interface for the Parking Citation Appeal Assistant.

## Features

- **Beautiful Landing Page**: Professional design with clear call-to-action
- **Interactive Form**: Step-by-step form to gather citation details
- **Real-time Processing**: AI-powered appeal generation with loading states
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **API Endpoints**: RESTful API for integration with other services

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the parent directory:

```
GOOGLE_GENERATIVE_AI_API_KEY=your_api_key_here
```

### 3. Run the Web Server

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
web/
├── app.py                  # Flask application
├── templates/              # HTML templates
│   ├── base.html          # Base template with header/footer
│   ├── index.html         # Landing page
│   ├── form.html          # Appeal creation form
│   └── about.html         # About page
├── static/                # Static assets
│   └── css/
│       └── style.css      # Styles
└── README.md              # This file
```

## API Endpoints

### GET /
Landing page with features and information

### GET /form
Appeal creation form

### GET /about
About page with detailed information

### GET /api/states
Returns list of supported states with details

**Response:**
```json
{
  "CA": {
    "code": "CA",
    "name": "California"
  },
  ...
}
```

### GET /api/cities/<state>
Returns cities for a specific state

**Response:**
```json
["San Francisco", "Los Angeles"]
```

### GET /api/appeal-angles
Returns all available appeal angles

**Response:**
```json
[
  {
    "key": "procedural_error",
    "name": "Procedural Error",
    "description": "Citation was issued incorrectly..."
  },
  ...
]
```

### POST /api/analyze
Analyzes citation and suggests appeal angles

**Request:**
```json
{
  "citation_number": "ABC123",
  "violation_type": "expired meter",
  "unclear_signage": true,
  "first_violation": true
}
```

**Response:**
```json
{
  "success": true,
  "suggested_angles": [
    {
      "key": "signage_issues",
      "name": "Inadequate or Confusing Signage",
      "description": "...",
      "questions": ["...", "..."]
    }
  ]
}
```

### POST /api/generate-appeal
Generates a parking citation appeal

**Request:**
```json
{
  "citation_number": "ABC123",
  "citation_date": "2024-01-15",
  "location": "123 Main St",
  "violation_type": "expired meter",
  "state": "CA",
  "city": "San Francisco",
  "first_violation": true,
  "unclear_signage": true,
  "evidence": ["photos_of_parking_location_and_signage"],
  "include_analysis": true
}
```

**Response:**
```json
{
  "success": true,
  "appeal": "Dear Parking Authority,\n\nI am writing to...",
  "analysis": "Based on the information provided...",
  "angles_used": ["Inadequate or Confusing Signage", "First-Time Violation"]
}
```

## Customization

### Styling

Edit `static/css/style.css` to customize colors, fonts, and layout.

CSS variables are defined at the top:
```css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    ...
}
```

### Templates

HTML templates use Jinja2 templating:
- `base.html` - Common layout for all pages
- `index.html` - Landing page content
- `form.html` - Appeal form with JavaScript
- `about.html` - Information about the app

### Adding New Features

1. Add route to `app.py`:
```python
@app.route('/new-page')
def new_page():
    return render_template('new_page.html')
```

2. Create template in `templates/new_page.html`

3. Update navigation in `base.html` if needed

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.app:app"]
```

### Environment Variables

Set these in production:
- `GOOGLE_GENERATIVE_AI_API_KEY` - Your Gemini API key
- `FLASK_ENV=production` - Disable debug mode
- `SECRET_KEY` - Set a secure random key

## Security Considerations

- Never commit `.env` file with real API keys
- Use HTTPS in production
- Set `app.secret_key` to a secure random value
- Implement rate limiting for API endpoints
- Validate and sanitize all user inputs
- Consider adding CSRF protection

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Responsive design

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Verify all dependencies are installed
- Check for syntax errors in `app.py`

### Appeals not generating
- Verify API key is set correctly in `.env`
- Check server logs for error messages
- Ensure internet connection for API calls

### Styling issues
- Clear browser cache
- Check browser console for CSS loading errors
- Verify `static/css/style.css` path is correct

## License

This web interface is part of the Parking Citation Appeal Assistant project.
For informational purposes only - not legal advice.

## Support

For issues or questions, please create an issue in the repository.
