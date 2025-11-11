document.addEventListener('DOMContentLoaded', function() {
    // Calendar functionality
    const initCalendar = () => {
        const calendarDays = document.querySelector('.grid.grid-cols-7.gap-1');
        if (!calendarDays) return;

        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        
        // Clear any existing days
        calendarDays.innerHTML = '';
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'h-8';
            calendarDays.appendChild(emptyDay);
        }
        
        // Add days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'h-8 flex items-center justify-center rounded-full cursor-pointer hover:bg-gray-100';
            
            // Highlight current day
            if (day === now.getDate() && currentMonth === now.getMonth()) {
                dayElement.classList.add('bg-indigo-600', 'text-white', 'font-medium');
            }
            
            dayElement.textContent = day;
            dayElement.addEventListener('click', () => {
                // Handle day click (e.g., filter tasks by date)
                console.log(`Selected date: ${currentMonth + 1}/${day}/${currentYear}`);
            });
            
            calendarDays.appendChild(dayElement);
        }
        
        // Update month/year display
        const monthYearElement = document.querySelector('.calendar-month-year');
        if (monthYearElement) {
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December'];
            monthYearElement.textContent = `${monthNames[currentMonth]} ${currentYear}`;
        }
    };

    // Toggle task completion
    const toggleTaskCompletion = (checkbox) => {
        const taskItem = checkbox.closest('li');
        if (checkbox.checked) {
            taskItem.classList.add('task-completed');
            // In a real app, update task status via API
            console.log('Task completed');
        } else {
            taskItem.classList.remove('task-completed');
            console.log('Task marked as incomplete');
        }
    };

    // Initialize task checkboxes
    const initTaskCheckboxes = () => {
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => toggleTaskCompletion(e.target));
        });
    };

    // Toggle mobile sidebar
    const initMobileSidebar = () => {
        const menuButton = document.querySelector('.mobile-menu-button');
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (menuButton && sidebar) {
            menuButton.addEventListener('click', (e) => {
                e.preventDefault();
                sidebar.classList.toggle('active');
                overlay?.classList.toggle('active');
                document.body.classList.toggle('overflow-hidden');
            });
        }
        
        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar?.classList.remove('active');
                overlay.classList.remove('active');
                document.body.classList.remove('overflow-hidden');
            });
        }
    };

    // Handle new task button
    const initNewTaskButton = () => {
        const newTaskBtn = document.querySelector('.new-task-btn');
        if (newTaskBtn) {
            newTaskBtn.addEventListener('click', (e) => {
                e.preventDefault();
                // In a real app, this would open a task creation modal
                console.log('New task button clicked');
                // For now, just show an alert
                alert('New task form would open here');
            });
        }
    };

    // Initialize calendar navigation
    const initCalendarNavigation = () => {
        const prevMonthBtn = document.querySelector('.calendar-nav-prev');
        const nextMonthBtn = document.querySelector('.calendar-nav-next');
        
        // These would be implemented to change the month
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Previous month');
                // Update calendar view
            });
        }
        
        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Next month');
                // Update calendar view
            });
        }
    };

    // Initialize everything
    const init = () => {
        initTaskCheckboxes();
        initMobileSidebar();
        initNewTaskButton();
        initCalendar();
        initCalendarNavigation();
        
        // Add animation to task items
        document.querySelectorAll('.task-item').forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('task-enter');
            }, index * 50);
        });
    };

    init();
});

// Utility function to format dates
function formatDate(dateString) {
    const options = { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Handle window resize for responsive behavior
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // Handle any responsive behavior here
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        // Close mobile menu when resizing to desktop
        if (window.innerWidth >= 768) {
            sidebar?.classList.remove('active');
            overlay?.classList.remove('active');
            document.body.classList.remove('overflow-hidden');
        }
    }, 250);
});
