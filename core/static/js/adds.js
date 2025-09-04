// ads.js - EduRise Advertisement Manager

class EduRiseAds {
    constructor(timerDuration = 30) {
        this.adElements = [];
        this.adTimers = new Map();
        this.timerDuration = timerDuration; // default countdown duration
        document.addEventListener('DOMContentLoaded', () => this.init());
    }

    init() {
        this.adElements = document.querySelectorAll('.ad-container, .sidebar-ad');
        this.adElements.forEach(ad => this.setupAd(ad));
        this.checkDismissedAds();
        this.setupAdAnalytics();
    }

    setupAd(adElement) {
        const adId = adElement.id;

        // Entry animation (tilt + fade-in)
        adElement.style.transform = 'translateY(30px) rotate(-1deg)';
        adElement.style.opacity = '0';
        setTimeout(() => {
            adElement.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
            adElement.style.transform = 'translateY(0) rotate(0deg)';
            adElement.style.opacity = '1';
        }, 100);

        // Highlight new ads temporarily
        if (!localStorage.getItem(`ad-${adId}-viewed`)) {
            adElement.classList.add('ad-highlight');
            localStorage.setItem(`ad-${adId}-viewed`, 'true');
            setTimeout(() => adElement.classList.remove('ad-highlight'), 5000);
        }

        // Countdown timer
        const counterElement = adElement.querySelector('.ad-counter');
        if (counterElement) this.startAdTimer(adId, counterElement, this.timerDuration);

        // Close button
        const closeButton = adElement.querySelector('.ad-close');
        if (closeButton) closeButton.addEventListener('click', () => this.closeAd(adId));

        // Hover tilt effect
        adElement.addEventListener('mouseenter', () => adElement.style.transform = 'rotate(-2deg) scale(1.03)');
        adElement.addEventListener('mouseleave', () => adElement.style.transform = 'rotate(0deg) scale(1)');

        // Track impressions
        this.trackAdEvent('ad_impression', adId);
    }

    startAdTimer(adId, counterElement, seconds) {
        let timeLeft = seconds;
        const timer = setInterval(() => {
            counterElement.textContent = `⏳ Closing in ${timeLeft}s`;
            timeLeft--;
            if (timeLeft < 0) this.closeAd(adId);
        }, 1000);
        this.adTimers.set(adId, timer);
    }

    closeAd(adId) {
        const adElement = document.getElementById(adId);
        if (!adElement) return;

        // Fade-out
        adElement.style.transition = 'opacity 0.5s ease';
        adElement.style.opacity = '0';
        setTimeout(() => {
            adElement.style.display = 'none';
            localStorage.setItem(`ad-${adId}-dismissed`, 'true');
            this.trackAdEvent('ad_dismissed', adId);
        }, 500);

        // Clear timer
        if (this.adTimers.has(adId)) {
            clearInterval(this.adTimers.get(adId));
            this.adTimers.delete(adId);
        }
    }

    checkDismissedAds() {
        this.adElements.forEach(ad => {
            const adId = ad.id;
            if (localStorage.getItem(`ad-${adId}-dismissed`) === 'true') {
                ad.style.display = 'none';
            }
        });
    }

    setupAdAnalytics() {
        document.querySelectorAll('.ad-cta').forEach(cta => {
            cta.addEventListener('click', e => {
                const adContainer = e.target.closest('.ad-container, .sidebar-ad');
                const adId = adContainer ? adContainer.id : 'unknown';
                this.trackAdEvent('ad_click', adId);
            });
        });
    }

    trackAdEvent(eventType, adId) {
        const eventData = {
            event: eventType,
            ad_id: adId,
            timestamp: new Date().toISOString(),
            page: window.location.pathname
        };
        console.log('Tracking ad event:', eventData);

        // Uncomment to send to backend analytics
        /*
        fetch('/api/analytics/ad-events', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(eventData)
        });
        */
    }

    showAd(adId) {
        const adElement = document.getElementById(adId);
        if (!adElement) return;
        localStorage.removeItem(`ad-${adId}-dismissed`);
        adElement.style.display = 'block';
        adElement.style.opacity = '1';
    }

    rotateAds(containerId, adsArray, interval = 10000) {
        const container = document.getElementById(containerId);
        if (!container || !adsArray.length) return;

        let index = 0;
        setInterval(() => {
            container.innerHTML = adsArray[index];
            index = (index + 1) % adsArray.length;
        }, interval);
    }
}

// Initialize globally
window.eduRiseAds = new EduRiseAds();
