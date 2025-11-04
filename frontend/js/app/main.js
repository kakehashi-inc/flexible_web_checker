
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.messages > div');
    if (messages.length > 0) {
        setTimeout(function() {
            messages.forEach(function(message) {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease-in-out';
                setTimeout(function() {
                    message.remove();
                }, 500);
            });
        }, 5000);
    }

    const checkButtons = document.querySelectorAll('.check-url-btn');
    checkButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const originalText = this.innerHTML;
            
            this.disabled = true;
            this.innerHTML = '<span class="spinner"></span> チェック中...';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('更新チェックを開始しました。', 'success');
                } else {
                    showNotification('エラーが発生しました。', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('エラーが発生しました。', 'error');
            })
            .finally(() => {
                this.disabled = false;
                this.innerHTML = originalText;
            });
        });
    });

    const collectionUrlButtons = document.querySelectorAll('.collection-url-btn');
    collectionUrlButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const action = this.getAttribute('data-action');
            const originalText = this.innerHTML;
            
            this.disabled = true;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (action === 'add') {
                        showNotification('URLをコレクションに追加しました。', 'success');
                        this.closest('tr').remove();
                    } else if (action === 'remove') {
                        showNotification('URLをコレクションから削除しました。', 'success');
                        this.closest('tr').remove();
                    }
                } else {
                    showNotification('エラーが発生しました。', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('エラーが発生しました。', 'error');
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.textContent = message;
    
    const container = document.querySelector('.messages');
    if (container) {
        container.appendChild(notification);
        
        setTimeout(function() {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease-in-out';
            setTimeout(function() {
                notification.remove();
            }, 500);
        }, 5000);
    }
}

function toggleHtmlCustomFields() {
    const checkTypeSelect = document.getElementById('id_check_type');
    const htmlSelectorField = document.getElementById('html-selector-field');
    const htmlConditionField = document.getElementById('html-condition-field');
    
    if (checkTypeSelect && htmlSelectorField && htmlConditionField) {
        function updateVisibility() {
            if (checkTypeSelect.value === 'HTML_CUSTOM') {
                htmlSelectorField.style.display = 'block';
                htmlConditionField.style.display = 'block';
            } else {
                htmlSelectorField.style.display = 'none';
                htmlConditionField.style.display = 'none';
            }
        }
        
        updateVisibility();
        checkTypeSelect.addEventListener('change', updateVisibility);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    toggleHtmlCustomFields();
});
