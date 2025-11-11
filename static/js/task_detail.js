document.addEventListener('DOMContentLoaded', function() {
    console.log('Task detail script loaded');
    
    // Get the task ID from the URL
    const taskId = window.location.pathname.split('/').pop();
    console.log('Task ID:', taskId);
    
    // Subtask functionality
    const showSubtaskFormBtn = document.getElementById('show-subtask-form');
    const subtaskForm = document.getElementById('subtask-form');
    const subtaskInput = document.getElementById('subtask-input');
    const addSubtaskBtn = document.getElementById('add-subtask');
    
    console.log('Subtask elements:', { showSubtaskFormBtn, subtaskForm, subtaskInput, addSubtaskBtn });
    
    if (showSubtaskFormBtn && subtaskForm) {
        showSubtaskFormBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Show subtask form clicked');
            subtaskForm.classList.toggle('hidden');
            if (!subtaskForm.classList.contains('hidden')) {
                subtaskInput.focus();
            }
        });
    }
    
    if (addSubtaskBtn && subtaskInput) {
        addSubtaskBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addSubtask();
        });
        
        subtaskInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSubtask();
            }
        });
    }
    
    // Label functionality
    const showLabelFormBtn = document.getElementById('show-label-form');
    const labelForm = document.getElementById('label-form');
    const labelInput = document.getElementById('label-input');
    const addLabelBtn = document.getElementById('add-label');
    const labelsContainer = document.querySelector('.flex.flex-wrap.gap-2');
    
    console.log('Label elements:', { showLabelFormBtn, labelForm, labelInput, addLabelBtn, labelsContainer });
    
    if (showLabelFormBtn && labelForm) {
        showLabelFormBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Show label form clicked');
            labelForm.classList.toggle('hidden');
            if (!labelForm.classList.contains('hidden')) {
                labelInput.focus();
            }
        });
    }
    
    if (addLabelBtn && labelInput) {
        addLabelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addLabel();
        });
        
        labelInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addLabel();
            }
        });
    }
    
    // Function to add a new subtask
    function addSubtask() {
        const title = subtaskInput.value.trim();
        if (!title) return;
        
        console.log('Adding subtask:', title);
        
        // In a real app, you would make an API call to your backend
        // For now, we'll just update the UI directly
        const subtaskList = document.querySelector('ul.space-y-2');
        
        if (subtaskList) {
            // Create a new subtask item
            const subtaskItem = document.createElement('li');
            subtaskItem.className = 'flex items-center p-3 bg-gray-50 rounded-lg';
            
            // Generate a unique ID for the new subtask
            const newId = Date.now();
            
            subtaskItem.innerHTML = `
                <input type="checkbox" class="h-5 w-5 text-indigo-600 rounded border-gray-300 mr-3">
                <span class="flex-1 text-gray-700">
                    ${title}
                </span>
                <button class="text-gray-400 hover:text-red-500 delete-subtask" data-id="${newId}">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            
            // If there's a "No subtasks" message, remove it
            const noSubtasksMsg = document.querySelector('.text-center.py-4.text-gray-400');
            if (noSubtasksMsg) {
                noSubtasksMsg.remove();
            }
            
            // If the subtask list doesn't exist, create it
            if (!subtaskList) {
                const subtasksContainer = document.querySelector('.space-y-6 > div:has(> h3:contains("Subtasks"))');
                if (subtasksContainer) {
                    const newSubtaskList = document.createElement('ul');
                    newSubtaskList.className = 'space-y-2';
                    newSubtaskList.appendChild(subtaskItem);
                    subtasksContainer.appendChild(newSubtaskList);
                }
            } else {
                subtaskList.prepend(subtaskItem);
            }
            
            // Clear the input
            subtaskInput.value = '';
            
            // Hide the form
            subtaskForm.classList.add('hidden');
            
            console.log('Subtask added');
        } else {
            console.error('Could not find subtask list');
        }
    }
    
    // Function to add a new label
    function addLabel() {
        const label = labelInput.value.trim();
        if (!label) return;
        
        console.log('Adding label:', label);
        
        // In a real app, you would make an API call to your backend
        // For now, we'll just update the UI directly
        
        // Create a new label element
        const labelElement = document.createElement('span');
        labelElement.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800';
        labelElement.textContent = label;
        
        // If there's a "No labels" message, remove it
        const noLabelsMsg = labelsContainer.querySelector('p.text-gray-400');
        if (noLabelsMsg) {
            noLabelsMsg.remove();
        }
        
        // Add the new label to the container
        labelsContainer.prepend(labelElement);
        
        // Clear the input
        labelInput.value = '';
        
        // Hide the form after adding
        labelForm.classList.add('hidden');
        
        console.log('Label added');
    }
    
    // Handle subtask completion toggle
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[type="checkbox"]') && e.target.closest('li.flex.items-center.p-3')) {
            const subtaskItem = e.target.closest('li');
            const subtaskText = subtaskItem.querySelector('span.flex-1');
            
            if (e.target.checked) {
                subtaskText.classList.add('line-through', 'text-gray-400');
                subtaskText.classList.remove('text-gray-700');
            } else {
                subtaskText.classList.remove('line-through', 'text-gray-400');
                subtaskText.classList.add('text-gray-700');
            }
        }
    });
    
    // Handle subtask deletion
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-subtask') || (e.target.matches('.fa-trash') && e.target.closest('button'))) {
            const button = e.target.closest('button');
            const subtaskItem = button.closest('li');
            const subtaskId = button.getAttribute('data-id');
            
            // In a real app, you would make an API call to delete the subtask
            subtaskItem.remove();
            
            // If no subtasks left, show a message
            const subtaskList = document.querySelector('ul.space-y-2');
            if (subtaskList && subtaskList.children.length === 0) {
                const noSubtasksMsg = document.createElement('div');
                noSubtasksMsg.className = 'text-center py-4 text-gray-400';
                noSubtasksMsg.innerHTML = '<p>No subtasks yet. Add one to get started!</p>';
                subtaskList.appendChild(noSubtasksMsg);
            }
        }
    });
});
