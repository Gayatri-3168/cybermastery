// ================= PHASE 1: QUICK WINS =================

// 1. Progress Animations
class ProgressAnimator {
    constructor() {
        this.progressBars = document.querySelectorAll('.progress-fill');
        this.xpCounters = document.querySelectorAll('.xp-counter');
        this.init();
    }

    init() {
        this.animateProgressBars();
        this.animateXPCounters();
        this.setupLevelUpAnimations();
    }

    animateProgressBars() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const progress = progressBar.dataset.progress || '0';
                    progressBar.style.setProperty('--progress', progress + '%');
                    progressBar.classList.add('animated');
                    observer.unobserve(progressBar);
                }
            });
        });

        this.progressBars.forEach(bar => observer.observe(bar));
    }

    animateXPCounters() {
        this.xpCounters.forEach(counter => {
            const targetXP = parseInt(counter.dataset.xp) || 0;
            const duration = 1000;
            const steps = 30;
            const increment = targetXP / steps;
            let currentXP = 0;

            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    const timer = setInterval(() => {
                        currentXP += increment;
                        if (currentXP >= targetXP) {
                            currentXP = targetXP;
                            clearInterval(timer);
                        }
                        counter.textContent = Math.floor(currentXP);
                    }, duration / steps);
                    observer.unobserve(counter);
                }
            });

            observer.observe(counter);
        });
    }

    setupLevelUpAnimations() {
        // Add level up celebration when XP reaches certain thresholds
        document.addEventListener('xpUpdated', (e) => {
            const newXP = e.detail.xp;
            const level = Math.floor(newXP / 100) + 1;
            
            if (newXP % 100 === 0) {
                this.celebrateLevelUp(level);
            }
        });
    }

    celebrateLevelUp(level) {
        const levelElements = document.querySelectorAll('.level-display');
        levelElements.forEach(el => {
            el.classList.add('level-up');
            setTimeout(() => el.classList.remove('level-up'), 1000);
        });

        // Show notification
        NotificationSystem.show({
            type: 'achievement',
            title: '🎉 Level Up!',
            message: `Congratulations! You've reached Level ${level}!`
        });
    }
}

// 2. Notification System
class NotificationSystem {
    static container = null;

    static init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        }
    }

    static show(options) {
        this.init();
        
        const notification = document.createElement('div');
        notification.className = `notification ${options.type || 'info'}`;
        
        notification.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">
                    <span class="notification-icon">${this.getIcon(options.type)}</span>
                    ${options.title || 'Notification'}
                </div>
                <button class="notification-close">×</button>
            </div>
            <div class="notification-message">${options.message}</div>
        `;

        this.container.appendChild(notification);

        // Auto remove after 5 seconds
        const timeout = setTimeout(() => this.remove(notification), 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            clearTimeout(timeout);
            this.remove(notification);
        });

        // Slide in animation
        setTimeout(() => notification.classList.add('show'), 10);
    }

    static remove(notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }

    static getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            achievement: '🏆',
            milestone: '🎯'
        };
        return icons[type] || icons.info;
    }

    static showAchievement(title, message) {
        this.show({
            type: 'achievement',
            title: '🏆 Achievement Unlocked!',
            message: `${title}: ${message}`
        });
    }

    static showMilestone(title, message) {
        this.show({
            type: 'milestone',
            title: '🎯 Milestone Reached!',
            message: `${title}: ${message}`
        });
    }
}

// 3. Search & Filter System
class SearchFilterSystem {
    constructor(container) {
        this.container = container;
        this.searchInput = container.querySelector('.search-input');
        this.filterChips = container.querySelectorAll('.filter-chip');
        this.sortDropdown = container.querySelector('.sort-dropdown');
        this.resultsContainer = container.querySelector('.search-results');
        this.activeFilters = new Set();
        this.searchTerm = '';
        this.sortBy = 'name';
        
        this.init();
    }

    init() {
        this.setupSearch();
        this.setupFilters();
        this.setupSorting();
        this.setupSuggestions();
    }

    setupSearch() {
        let searchTimeout;
        
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            this.searchTerm = e.target.value.toLowerCase();
            
            searchTimeout = setTimeout(() => {
                this.performSearch();
                this.showSuggestions(this.searchTerm);
            }, 300);
        });

        this.searchInput.addEventListener('focus', () => {
            if (this.searchTerm) {
                this.showSuggestions(this.searchTerm);
            }
        });

        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    setupFilters() {
        this.filterChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const filter = chip.dataset.filter;
                
                if (chip.classList.contains('active')) {
                    chip.classList.remove('active');
                    this.activeFilters.delete(filter);
                } else {
                    chip.classList.add('active');
                    this.activeFilters.add(filter);
                }
                
                this.updateFilterTags();
                this.performSearch();
            });
        });
    }

    setupSorting() {
        if (this.sortDropdown) {
            this.sortDropdown.addEventListener('change', (e) => {
                this.sortBy = e.target.value;
                this.performSearch();
            });
        }
    }

    setupSuggestions() {
        // Create suggestions container
        this.suggestionsContainer = document.createElement('div');
        this.suggestionsContainer.className = 'search-suggestions';
        this.searchInput.parentNode.appendChild(this.suggestionsContainer);
    }

    performSearch() {
        const items = this.getSearchableItems();
        const filteredItems = this.filterItems(items);
        const sortedItems = this.sortItems(filteredItems);
        
        this.displayResults(sortedItems);
        this.updateResultsCount(sortedItems.length);
    }

    getSearchableItems() {
        // This should be implemented based on your specific data structure
        return Array.from(document.querySelectorAll('[data-searchable]')).map(el => ({
            element: el,
            name: el.dataset.name || el.textContent.toLowerCase(),
            category: el.dataset.category || '',
            difficulty: el.dataset.difficulty || '',
            completed: el.dataset.completed === 'true'
        }));
    }

    filterItems(items) {
        return items.filter(item => {
            // Search term filter
            if (this.searchTerm && !item.name.includes(this.searchTerm)) {
                return false;
            }

            // Active filters
            for (const filter of this.activeFilters) {
                if (!item.category.includes(filter) && !item.difficulty.includes(filter)) {
                    return false;
                }
            }

            return true;
        });
    }

    sortItems(items) {
        return items.sort((a, b) => {
            switch (this.sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'difficulty':
                    return a.difficulty.localeCompare(b.difficulty);
                case 'completed':
                    return b.completed - a.completed;
                default:
                    return 0;
            }
        });
    }

    displayResults(items) {
        // Hide all items first
        this.getSearchableItems().forEach(item => {
            item.element.style.display = 'none';
        });

        // Show filtered items
        items.forEach(item => {
            item.element.style.display = '';
        });
    }

    updateResultsCount(count) {
        if (this.resultsContainer) {
            this.resultsContainer.textContent = `Found ${count} result${count !== 1 ? 's' : ''}`;
            this.resultsContainer.className = count > 0 ? 'search-results active' : 'search-results';
        }
    }

    updateFilterTags() {
        const tagsContainer = this.container.querySelector('.filter-tags');
        if (!tagsContainer) return;

        tagsContainer.innerHTML = '';
        
        this.activeFilters.forEach(filter => {
            const tag = document.createElement('div');
            tag.className = 'filter-tag';
            tag.innerHTML = `
                ${filter}
                <button class="filter-tag-remove">×</button>
            `;
            
            tag.querySelector('.filter-tag-remove').addEventListener('click', () => {
                const chip = this.container.querySelector(`[data-filter="${filter}"]`);
                if (chip) chip.click();
            });
            
            tagsContainer.appendChild(tag);
        });
    }

    showSuggestions(term) {
        // This should be implemented with actual suggestion data
        const suggestions = this.getSuggestions(term);
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsContainer.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" data-value="${suggestion}">
                ${this.highlightMatch(suggestion, term)}
            </div>
        `).join('');

        this.suggestionsContainer.classList.add('active');

        // Add click handlers
        this.suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.searchInput.value = item.dataset.value;
                this.searchTerm = item.dataset.value.toLowerCase();
                this.performSearch();
                this.hideSuggestions();
            });
        });
    }

    hideSuggestions() {
        this.suggestionsContainer.classList.remove('active');
    }

    getSuggestions(term) {
        // This should return actual suggestions based on your data
        const allItems = this.getSearchableItems();
        const suggestions = new Set();
        
        allItems.forEach(item => {
            if (item.name.includes(term)) {
                suggestions.add(item.name);
            }
        });

        return Array.from(suggestions).slice(0, 5);
    }

    highlightMatch(text, term) {
        const regex = new RegExp(`(${term})`, 'gi');
        return text.replace(regex, '<span class="suggestion-highlight">$1</span>');
    }
}

// 4. Achievement System
class AchievementSystem {
    constructor() {
        this.achievements = [];
        this.unlockedAchievements = new Set();
        this.container = document.querySelector('.achievements-container');
        this.init();
    }

    init() {
        this.loadAchievements();
        this.setupAchievementListeners();
        this.checkAchievements();
    }

    loadAchievements() {
        // This should load achievements from your backend
        this.achievements = [
            {
                id: 'first_mission',
                name: 'First Steps',
                description: 'Complete your first mission',
                icon: '🚀',
                category: 'missions',
                rarity: 'common',
                requirement: { type: 'missions_completed', value: 1 }
            },
            {
                id: 'cyber_expert',
                name: 'Cyber Expert',
                description: 'Complete 5 missions',
                icon: '🛡️',
                category: 'missions',
                rarity: 'rare',
                requirement: { type: 'missions_completed', value: 5 }
            },
            {
                id: 'perfectionist',
                name: 'Perfectionist',
                description: 'Complete 10 missions without mistakes',
                icon: '⭐',
                category: 'missions',
                rarity: 'epic',
                requirement: { type: 'perfect_missions', value: 10 }
            },
            {
                id: 'speed_demon',
                name: 'Speed Demon',
                description: 'Complete a mission in under 2 minutes',
                icon: '⚡',
                category: 'missions',
                rarity: 'rare',
                requirement: { type: 'speed_run', value: 120 }
            }
        ];
    }

    setupAchievementListeners() {
        // Listen for game events
        document.addEventListener('missionCompleted', (e) => {
            this.checkAchievements();
        });

        document.addEventListener('xpUpdated', (e) => {
            this.checkAchievements();
        });

        document.addEventListener('levelUp', (e) => {
            this.checkAchievements();
        });
    }

    checkAchievements() {
        this.achievements.forEach(achievement => {
            if (!this.unlockedAchievements.has(achievement.id) && this.isAchievementUnlocked(achievement)) {
                this.unlockAchievement(achievement);
            }
        });
    }

    isAchievementUnlocked(achievement) {
        // This should check against actual user progress
        const userProgress = this.getUserProgress();
        
        switch (achievement.requirement.type) {
            case 'missions_completed':
                return userProgress.missionsCompleted >= achievement.requirement.value;
            case 'perfect_missions':
                return userProgress.perfectMissions >= achievement.requirement.value;
            case 'speed_run':
                return userProgress.fastestTime <= achievement.requirement.value;
            case 'xp_earned':
                return userProgress.totalXP >= achievement.requirement.value;
            default:
                return false;
        }
    }

    getUserProgress() {
        // This should get actual user progress from your backend
        return {
            missionsCompleted: parseInt(localStorage.getItem('missionsCompleted') || '0'),
            perfectMissions: parseInt(localStorage.getItem('perfectMissions') || '0'),
            fastestTime: parseInt(localStorage.getItem('fastestTime') || '999'),
            totalXP: parseInt(localStorage.getItem('totalXP') || '0')
        };
    }

    unlockAchievement(achievement) {
        this.unlockedAchievements.add(achievement.id);
        
        // Show popup
        this.showAchievementPopup(achievement);
        
        // Show notification
        NotificationSystem.showAchievement(achievement.name, achievement.description);
        
        // Update UI
        this.updateAchievementCard(achievement);
        
        // Save to backend
        this.saveUnlockedAchievement(achievement.id);
    }

    showAchievementPopup(achievement) {
        const popup = document.createElement('div');
        popup.className = 'achievement-popup';
        popup.innerHTML = `
            <div class="achievement-popup-icon">${achievement.icon}</div>
            <div class="achievement-popup-title">Achievement Unlocked!</div>
            <div class="achievement-popup-text">${achievement.name}</div>
            <div class="achievement-popup-actions">
                <a href="${this.getBadgeImageUrl(achievement)}" 
                   download="${this.getBadgeFileName(achievement)}" 
                   class="achievement-popup-download">
                    📥 Download Badge
                </a>
                <button class="achievement-popup-close" onclick="this.parentElement.parentElement.remove()">Awesome!</button>
            </div>
        `;

        document.body.appendChild(popup);

        // Auto remove after 8 seconds
        setTimeout(() => popup.remove(), 8000);
    }

    getBadgeImageUrl(achievement) {
        // Generate the URL for the badge image
        const badgeName = achievement.name.toLowerCase().replace(/\s+/g, '_');
        return `/static/images/badges/${badgeName}.png`;
    }

    getBadgeFileName(achievement) {
        // Generate a user-friendly filename for download
        const badgeName = achievement.name.toLowerCase().replace(/\s+/g, '_');
        return `${badgeName}_badge.png`;
    }

    updateAchievementCard(achievement) {
        const card = document.querySelector(`[data-achievement="${achievement.id}"]`);
        if (card) {
            card.classList.remove('locked');
            card.classList.add('unlocked', achievement.rarity);
            
            // Add NEW badge
            const badge = document.createElement('div');
            badge.className = 'achievement-badge new';
            badge.textContent = 'NEW';
            card.appendChild(badge);
        }
    }

    saveUnlockedAchievement(achievementId) {
        // This should save to your backend
        const unlocked = JSON.parse(localStorage.getItem('unlockedAchievements') || '[]');
        unlocked.push(achievementId);
        localStorage.setItem('unlockedAchievements', JSON.stringify(unlocked));
    }

    renderAchievements() {
        if (!this.container) return;

        const grid = this.container.querySelector('.achievements-grid');
        if (!grid) return;

        grid.innerHTML = this.achievements.map(achievement => {
            const isUnlocked = this.unlockedAchievements.has(achievement.id);
            const progress = this.getAchievementProgress(achievement);
            
            return `
                <div class="achievement-card ${isUnlocked ? 'unlocked' : 'locked'} ${achievement.rarity}" 
                     data-achievement="${achievement.id}">
                    <div class="achievement-icon">${achievement.icon}</div>
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                    ${!isUnlocked ? `
                        <div class="achievement-progress">
                            <div class="progress-text">${progress.text}</div>
                            <div class="progress-bar-small">
                                <div class="progress-fill-small" style="width: ${progress.percentage}%"></div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        // Add click handlers for detail modal
        grid.querySelectorAll('.achievement-card').forEach(card => {
            card.addEventListener('click', () => {
                const achievementId = card.dataset.achievement;
                const achievement = this.achievements.find(a => a.id === achievementId);
                if (achievement) {
                    this.showAchievementDetail(achievement);
                }
            });
        });
    }

    getAchievementProgress(achievement) {
        const userProgress = this.getUserProgress();
        let current = 0;
        let total = achievement.requirement.value;

        switch (achievement.requirement.type) {
            case 'missions_completed':
                current = userProgress.missionsCompleted;
                break;
            case 'perfect_missions':
                current = userProgress.perfectMissions;
                break;
            case 'speed_run':
                current = Math.min(userProgress.fastestTime, achievement.requirement.value);
                break;
            case 'xp_earned':
                current = userProgress.totalXP;
                break;
        }

        const percentage = Math.min((current / total) * 100, 100);
        return {
            current,
            total,
            percentage,
            text: `${current}/${total}`
        };
    }

    showAchievementDetail(achievement) {
        const modal = document.createElement('div');
        modal.className = 'achievement-detail-modal active';
        
        const isUnlocked = this.unlockedAchievements.has(achievement.id);
        const progress = this.getAchievementProgress(achievement);
        
        modal.innerHTML = `
            <div class="achievement-detail-content">
                <div class="achievement-detail-icon">${achievement.icon}</div>
                <div class="achievement-detail-title">${achievement.name}</div>
                <div class="achievement-detail-description">${achievement.description}</div>
                <div class="achievement-detail-reward">
                    <div class="reward-title">Reward</div>
                    <div class="reward-text">+${this.getRewardXP(achievement)} XP</div>
                </div>
                ${!isUnlocked ? `
                    <div class="achievement-progress">
                        <div class="progress-text">Progress: ${progress.text}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress.percentage}%"></div>
                        </div>
                    </div>
                ` : '<div style="color: #22c55e; font-weight: 600;">✅ Completed!</div>'}
                <button class="close-modal" onclick="this.closest('.achievement-detail-modal').remove()">Close</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    getRewardXP(achievement) {
        const rewards = {
            common: 10,
            rare: 25,
            epic: 50,
            legendary: 100
        };
        return rewards[achievement.rarity] || 10;
    }
}

// ================= INITIALIZATION =================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all systems
    const progressAnimator = new ProgressAnimator();
    NotificationSystem.init();
    
    // Initialize search/filter if containers exist
    document.querySelectorAll('.search-filter-container').forEach(container => {
        new SearchFilterSystem(container);
    });
    
    // Initialize achievement system
    const achievementSystem = new AchievementSystem();
    
    // Global event handlers for demo purposes
    window.showNotification = NotificationSystem.show.bind(NotificationSystem);
    window.achievementSystem = achievementSystem;
});

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ProgressAnimator,
        NotificationSystem,
        SearchFilterSystem,
        AchievementSystem
    };
}
