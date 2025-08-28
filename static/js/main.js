/**
 * Paper Finder - 主JavaScript文件
 * 提供全局UI交互功能
 */

// 当文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化搜索表单验证
    initializeFormValidation();
    
    // 初始化示例问题点击事件
    initializeExampleQuestions();
    
    // 添加平滑滚动效果
    initializeSmoothScroll();
});

/**
 * 初始化Bootstrap工具提示
 */
function initializeTooltips() {
    // 检查是否有Bootstrap的tooltip函数
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    // 获取所有需要验证的表单
    const forms = document.querySelectorAll('.needs-validation');
    
    // 遍历表单并添加验证
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * 初始化示例问题点击事件
 */
function initializeExampleQuestions() {
    // 获取所有示例问题元素
    const exampleQuestions = document.querySelectorAll('.example-question');
    
    // 为每个示例问题添加点击事件
    exampleQuestions.forEach(question => {
        question.addEventListener('click', function(event) {
            event.preventDefault();
            
            // 获取问题文本
            const questionText = this.textContent.trim();
            
            // 查找搜索输入框并设置值
            const searchInput = document.getElementById('question');
            if (searchInput) {
                searchInput.value = questionText;
                
                // 如果存在表单，则提交
                const form = searchInput.closest('form');
                if (form) {
                    // 使用jQuery提交表单（如果可用）
                    if (typeof $ !== 'undefined') {
                        $(form).submit();
                    } else {
                        form.submit();
                    }
                }
            }
        });
    });
}

/**
 * 初始化平滑滚动效果
 */
function initializeSmoothScroll() {
    // 获取所有带有href属性的锚点链接
    const scrollLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    // 为每个链接添加点击事件
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            // 检查链接是否指向页面内部
            if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && 
                location.hostname === this.hostname) {
                
                // 获取目标元素
                const target = document.querySelector(this.hash);
                if (target) {
                    event.preventDefault();
                    
                    // 平滑滚动到目标位置
                    window.scrollTo({
                        top: target.offsetTop - 70, // 减去导航栏高度
                        behavior: 'smooth'
                    });
                    
                    // 更新URL但不滚动
                    history.pushState(null, null, this.hash);
                }
            }
        });
    });
}

/**
 * 显示加载动画
 * @param {HTMLElement} container - 要显示加载动画的容器元素
 */
function showLoading(container) {
    // 创建加载动画元素
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');
    
    const spinnerText = document.createElement('span');
    spinnerText.className = 'visually-hidden';
    spinnerText.textContent = '加载中...';
    
    spinner.appendChild(spinnerText);
    
    // 清空容器并添加加载动画
    container.innerHTML = '';
    container.appendChild(spinner);
}

/**
 * 显示错误消息
 * @param {HTMLElement} container - 要显示错误消息的容器元素
 * @param {string} message - 错误消息文本
 */
function showError(container, message) {
    // 创建错误消息元素
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger';
    alert.textContent = message || '发生错误，请重试。';
    
    // 清空容器并添加错误消息
    container.innerHTML = '';
    container.appendChild(alert);
}

/**
 * 格式化日期时间
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
        return dateString; // 返回原始字符串
    }
    
    // 格式化日期
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}