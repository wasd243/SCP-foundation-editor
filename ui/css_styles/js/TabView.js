function selectTab(btn) {
    const header = btn.parentElement;
    const box = header.parentElement;
    const index = Array.from(header.children).indexOf(btn);

    Array.from(header.querySelectorAll('.tab-btn')).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const contents = box.querySelector('.tab-contents');
    Array.from(contents.children).forEach((c, i) => {
        c.classList.toggle('active', i === index);
    });
}

function addTab(btn) {
    const header = btn.parentElement;
    const box = header.parentElement;
    const contents = box.querySelector('.tab-contents');
    const newBtn = document.createElement('span');
    newBtn.className = 'tab-btn';
    newBtn.setAttribute('contenteditable', 'true');
    newBtn.onclick = function () { selectTab(this); };
    newBtn.innerText = 'New Tab';
    header.insertBefore(newBtn, btn);
    const newContent = document.createElement('div');
    newContent.className = 'tab-item';
    newContent.setAttribute('contenteditable', 'true');
    newContent.innerHTML = '<p>Tab Content...</p>';
    contents.appendChild(newContent);
    selectTab(newBtn);
}

function removeTab(btn) {
    const header = btn.parentElement;
    const box = header.closest('.tabview-box');
    const index = Array.from(header.children).indexOf(btn);
    const contents = box.querySelector('.tab-contents');
    if (header.querySelectorAll('.tab-btn').length <= 1) {
        alert('至少保留一个选项卡');
        return;
    }
    btn.remove();
    if (contents.children[index]) contents.children[index].remove();
    const firstBtn = header.querySelector('.tab-btn');
    if (firstBtn) selectTab(firstBtn);
}