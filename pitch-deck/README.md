# Communication Bridge AI - Pitch Deck

Interactive HTML/CSS/JavaScript presentation for project submission.

## 📁 Files

- `index.html` - Main presentation structure (15 slides)
- `styles.css` - Complete styling and responsive design
- `script.js` - Navigation and interactive features
- `README.md` - This file

## 🚀 How to Use

### Open the Presentation

1. **Local**: Open `index.html` in any modern browser
2. **Server**: Host on any web server (GitHub Pages, Netlify, etc.)

### Navigation

**Mouse/Touch:**
- Click ← → buttons at bottom
- Swipe left/right on mobile devices

**Keyboard Shortcuts:**
- `→` or `Space` - Next slide
- `←` - Previous slide
- `Home` - First slide
- `End` - Last slide
- `F` - Toggle fullscreen
- `P` - Print presentation
- `O` - Overview mode (see all slides)
- `A` - Auto-advance toggle (10 sec/slide)
- `H` - Show help menu
- `ESC` - Exit fullscreen/overview

## 📊 Slide Contents

1. **Title** - Communication Bridge AI branding
2. **Problem** - Market statistics and pain points
3. **Solution** - AI-powered translation features
4. **Key Features** - 4 main capabilities
5. **Gestures** - All 18 supported gestures
6. **How It Works** - Bidirectional flow diagrams
7. **Market** - $28B TAM breakdown
8. **Business Model** - Pricing tiers
9. **Competitive Advantage** - Comparison table
10. **Traction** - Milestones and roadmap
11. **Financials** - 3-year projections
12. **Funding** - $500K seed round breakdown
13. **Social Impact** - UN SDG alignment
14. **Demo** - Live demo link and QR code
15. **Contact** - Contact info and CTA

## 🎨 Customization

### Update Contact Info (Slide 15)

Edit `index.html` line ~580:

```html
<div class="contact-item">
    <span class="contact-icon">📧</span>
    <span class="contact-text">your.email@example.com</span>
</div>
```

### Change Colors

Edit `styles.css` gradient colors:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Add QR Code (Slide 14)

Replace the QR placeholder with actual QR code image:

```html
<div class="qr-placeholder">
    <img src="qr-code.png" alt="Demo QR Code" style="width: 100%; height: 100%;">
</div>
```

Generate QR code for: `https://3001-i1jp0gsn9.brevlab.com`

## 📱 Responsive Design

- **Desktop**: Full-featured presentation
- **Tablet**: 2-column layouts
- **Mobile**: Single-column, swipe navigation

## 🖨️ Print Mode

Press `P` or use browser print (Ctrl+P / Cmd+P) to print all slides.

## 🌐 Hosting Options

### GitHub Pages (Free)

1. Create new repo: `communication-bridge-pitch`
2. Upload pitch-deck files
3. Enable GitHub Pages in Settings
4. Access at: `https://yourusername.github.io/communication-bridge-pitch/`

### Netlify (Free)

1. Drag & drop `pitch-deck` folder to Netlify
2. Get instant URL: `https://random-name.netlify.app`
3. Optional: Add custom domain

### Vercel (Free)

```bash
cd pitch-deck
vercel
```

## 🎯 Presentation Tips

1. **Practice**: Run through all 15 slides (aim for 10-15 minutes)
2. **Fullscreen**: Press `F` for distraction-free presenting
3. **Auto-advance**: Press `A` to auto-advance every 10 seconds
4. **Demo**: Have live demo ready on Slide 14
5. **Questions**: Pause on relevant slides for Q&A

## 📈 Analytics

The script tracks:
- Slide views (console log)
- Presentation time
- Navigation patterns

Check browser console for stats:

```javascript
// Get current slide
pitchDeck.getCurrentSlide()

// Get slide view counts
pitchDeck.getSlideViews()

// Jump to specific slide
pitchDeck.goToSlide(5)
```

## 🔧 Troubleshooting

**Slides not showing:**
- Check browser console for errors
- Ensure all 3 files are in same directory
- Try different browser (Chrome, Firefox, Safari)

**Navigation not working:**
- Refresh page
- Check JavaScript is enabled
- Clear browser cache

**Styling issues:**
- Ensure `styles.css` is loaded
- Check file paths are correct
- Try hard refresh (Ctrl+Shift+R)

## 📝 Notes

- All content from `PITCH_DECK.md` is included
- Fully responsive and mobile-friendly
- No external dependencies (works offline)
- Print-friendly layout
- Accessibility features included

## 🎓 For Submission

Include these files:
- ✅ `index.html`
- ✅ `styles.css`
- ✅ `script.js`
- ✅ `README.md`
- ✅ `PITCH_DECK.md` (reference)

Optional:
- QR code image for demo link
- Screenshots of each slide
- PDF export of presentation

## 📞 Support

For issues or questions:
- Check browser console for errors
- Review `PITCH_DECK.md` for content reference
- Test in different browsers

---

**Good luck with your presentation! 🚀**
