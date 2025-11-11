document.addEventListener('DOMContentLoaded', function() {
    console.log('Home page script loaded');
    
    // Task completion toggle
    setupTaskCompletion();
    
    // Add task button handlers
    setupAddTaskButtons();
    
    // Task filtering and search
    setupTaskFiltering();
    
    // Mobile menu toggle
    setupMobileMenu();
    
    // Initialize tooltips
    initializeTooltips();
});

function setupTaskCompletion() {
    // Handle task completion toggle
    document.addEventListener('change', function(e) {
        const checkbox = e.target;
        if (checkbox.matches('.task-item input[type="checkbox"]')) {
            const taskItem = checkbox.closest('.task-item');
            const taskTitle = taskItem.querySelector('a');
            const taskId = taskTitle.getAttribute('href').split('/').pop();
            
            // Toggle visual feedback
            if (checkbox.checked) {
                taskTitle.classList.add('line-through', 'text-gray-400');
                // In a real app, you would make an API call to update the task status
                console.log(`Marking task ${taskId} as completed`);
            } else {
                taskTitle.classList.remove('line-through', 'text-gray-400');
                console.log(`Marking task ${taskId} as incomplete`);
            }
            
            // In a real app, you would update the task status via an API call
            // updateTaskStatus(taskId, checkbox.checked);
        }
    });
}

function setupAddTaskButtons() {
    // Desktop add task button
    const desktopAddBtn = document.querySelector('.task-list-header button');
    // Mobile add task button
    const mobileAddBtn = document.querySelector('.new-task-btn');
    
    const showAddTaskForm = () => {
        // In a real app, this would show a modal or slide-in form
        console.log('Show add task form');
        alert('Add task functionality will be implemented here');
    };
    
    if (desktopAddBtn) desktopAddBtn.addEventListener('click', showAddTaskForm);
    if (mobileAddBtn) mobileAddBtn.addEventListener('click', showAddTaskForm);
}

function setupTaskFiltering() {
    // This would be connected to a search input if available
    const searchInput = document.querySelector('input[type="search"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const tasks = document.querySelectorAll('.task-item');
            
            tasks.forEach(task => {
                const title = task.querySelector('a').textContent.toLowerCase();
                const description = task.querySelector('p.text-gray-600')?.textContent.toLowerCase() || '';
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    task.style.display = '';
                } else {
                    task.style.display = 'none';
                }
            });
        });
    }
    
    // Filter by priority if filter buttons exist
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const priority = this.getAttribute('data-priority');
            const tasks = document.querySelectorAll('.task-item');
            
            tasks.forEach(task => {
                const taskPriority = task.querySelector('.priority-badge')?.textContent.trim().toLowerCase();
                if (!priority || taskPriority === priority) {
                    task.style.display = '';
                } else {
                    task.style.display = 'none';
                }
            });
            
            // Update active filter button
            filterButtons.forEach(b => b.classList.remove('bg-indigo-100', 'text-indigo-700'));
            if (priority) {
                this.classList.add('bg-indigo-100', 'text-indigo-700');
            }
        });
    });
}

function setupMobileMenu() {
    const mobileMenuButton = document.querySelector('[aria-controls="mobile-menu"]');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const expanded = this.getAttribute('aria-expanded') === 'true' || false;
            this.setAttribute('aria-expanded', !expanded);
            mobileMenu.classList.toggle('hidden');
        });
    }
}

function initializeTooltips() {
    // Initialize any tooltips if using a library like Tippy.js
    // Example: tippy('[data-tippy-content]');
    
    // Simple title-based tooltips
    const elementsWithTooltips = document.querySelectorAll('[title]');
    elementsWithTooltips.forEach(el => {
        el.addEventListener('mouseenter', function() {
            // In a real app, you might want to use a proper tooltip library
            console.log('Show tooltip:', this.title);
        });
    });
}

// In a real app, you would have API functions like:
/*
async function updateTaskStatus(taskId, completed) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ completed })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task status');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating task status:', error);
        // Show error message to user
    }
}
*/
