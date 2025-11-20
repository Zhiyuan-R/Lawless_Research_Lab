# Quick Start Guide

Get started with the Parking Citation Appeal Assistant in 3 easy steps!

## Option 1: Web Interface (Recommended for First-Time Users)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Your API Key
Create a `.env` file:
```bash
echo "GOOGLE_GENERATIVE_AI_API_KEY=AIzaSyBFoHyKjCJSeXZiGJS6jJdfmJYKftB0cbE" > .env
```

### Step 3: Launch the Web App
```bash
cd web
python app.py
```

### Step 4: Open Your Browser
Visit: **http://localhost:5000**

That's it! You now have a beautiful web interface where you can:
- Fill out an interactive form
- Generate AI-powered appeals
- Copy appeals to clipboard
- View case analysis

---

## Option 2: Command-Line Interface

### For Interactive Experience:
```bash
python main.py
```
Follow the prompts to create your appeal.

### For Quick Testing:
```bash
python main.py --quick --citation ABC123 --state CA --violation "expired meter"
```

---

## Option 3: See Examples Without API Calls

Run the demo to see features without using API:
```bash
python demo_without_api.py
```

---

## What to Prepare

Before creating your appeal, gather:

1. **Citation Details**
   - Citation number
   - Date and time
   - Location
   - Violation type
   - Fine amount

2. **Evidence** (if available)
   - Photos of parking spot and signage
   - Photos of citation
   - Parking receipts
   - Payment confirmations
   - Meter photos

3. **Your Story**
   - What happened?
   - Why do you believe the citation is unfair?
   - Any emergency or special circumstances?

---

## Need Help?

- **Web Interface Issues**: See `web/README.md`
- **CLI Issues**: See main `README.md`
- **API Key Problems**: Make sure `.env` file exists in project root
- **General Questions**: Check the About page in the web interface

---

## Pro Tips

✓ **Take Photos**: Always photograph parking spots, signs, and meters
✓ **Act Fast**: Most jurisdictions have 21-30 day appeal deadlines
✓ **Be Honest**: Only claim what you can support with evidence
✓ **Review Carefully**: Customize the AI-generated appeal before submitting
✓ **Keep Copies**: Save all documents and correspondence

---

## Test Data for Demo

If you want to test the app, use these sample values:

- **Citation Number**: TEST123
- **Date**: Today's date
- **Location**: 123 Main Street, San Francisco
- **Violation**: Expired Meter
- **State**: CA
- **City**: San Francisco
- **Situation**: Check "Unclear signage" and "First violation"

This will generate a realistic appeal letter you can review.

---

**Good luck with your parking citation appeal!**

For full documentation, see `README.md`
