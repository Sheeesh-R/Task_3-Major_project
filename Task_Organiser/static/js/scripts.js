// Task Organiser App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Task status toggle handler
    document.querySelectorAll('.task-status-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const status = this.checked ? 'completed' : 'not_started';
            
            fetch(`/task/${taskId}/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI to reflect the change
                    const taskItem = this.closest('.task-item');
                    if (status === 'completed') {
                        taskItem.classList.add('completed');
                        this.checked = true;
                    } else {
                        taskItem.classList.remove('completed');
                        this.checked = false;
                    }
                    // Show success message
                    showAlert('Task status updated!', 'success');
                } else {
                    // Revert the checkbox if the update failed
                    this.checked = !this.checked;
                    showAlert('Failed to update task status', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !this.checked;
                showAlert('An error occurred', 'danger');
            });
        });
    });

    // Delete task handler
    document.querySelectorAll('.delete-task').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this task?')) {
                const taskId = this.dataset.taskId;
                fetch(`/task/${taskId}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the task from the UI
                        const taskItem = this.closest('.task-item');
                        taskItem.style.opacity = '0';
                        setTimeout(() => {
                            taskItem.remove();
                            showAlert('Task deleted successfully!', 'success');
                        }, 300);
                    } else {
                        showAlert('Failed to delete task', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred', 'danger');
                });
            }
        });
    });

    // Show alert function
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Initialize date pickers
    if (flatpickr) {
        flatpickr("input[type='date']", {
            dateFormat: "Y-m-d",
            allowInput: true
        });
    }
});

// Calendar functionality
let currentDate = new Date();
const prevBtn = document.getElementById('prev-month');
const nextBtn = document.getElementById('next-month');
const todayBtn = document.getElementById('today');
const monthYearElement = document.getElementById('current-month-year');
const daysContainer = document.getElementById('calendar-days');

if (prevBtn && nextBtn && todayBtn && monthYearElement && daysContainer) {
    // Get all task due dates from the page
    const taskDateElements = document.querySelectorAll('.task-due-date');
    const taskDates = Array.from(taskDateElements).map(el => {
        const dateStr = el.getAttribute('data-due-date');
        return dateStr ? new Date(dateStr) : null;
    }).filter(date => date);

    function renderCalendar() {
        // Clear previous calendar days
        daysContainer.innerHTML = '';
        
        // Set month and year in header
        const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                       'August', 'September', 'October', 'November', 'December'];
        monthYearElement.textContent = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        
        // Get first day of month and total days in month
        const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
        const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
        const daysInMonth = lastDay.getDate();
        
        // Get day of week for first day of month (0 = Sunday, 1 = Monday, etc.)
        const startingDay = firstDay.getDay();
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < startingDay; i++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day empty';
            daysContainer.appendChild(dayElement);
        }
        
        // Add days of the month
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            // Check if current day is today
            const currentDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            if (currentDay.toDateString() === today.toDateString()) {
                dayElement.classList.add('today');
            }
            
            // Check if there are tasks due on this day
            const hasTasks = taskDates.some(date => {
                return date.getDate() === day && 
                       date.getMonth() === currentDate.getMonth() && 
                       date.getFullYear() === currentDate.getFullYear();
            });
            
            if (hasTasks) {
                dayElement.classList.add('has-tasks');
            }
            
            daysContainer.appendChild(dayElement);
        }
    }
    
    // Navigation event listeners
    prevBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });
    
    nextBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    todayBtn.addEventListener('click', () => {
        currentDate = new Date();
        renderCalendar();
    });
    
    // Initial render
    renderCalendar();
}
