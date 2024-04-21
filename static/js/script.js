if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
} else {
    document.documentElement.classList.remove('dark')
}

localStorage.theme = 'light'
localStorage.theme = 'dark'
localStorage.removeItem('theme')


function displayImage(inputElement) {
    const file = inputElement.files[0];
    const imageURL = URL.createObjectURL(file);
    document.getElementById('preview').src = imageURL;
    document.getElementById('preview').onload = () => URL.revokeObjectURL(imageURL);
}


function sendMessage() {
        var xhr = new XMLHttpRequest();
        var url = '/message_send'; // URL, куда отправляется POST запрос
        xhr.open('POST', url, true);
        var formData = new FormData(document.getElementById('messageForm'));
        xhr.onreadystatechange = function() {
          console.log(xhr.readyState)
          console.log(xhr.status)
          if(xhr.readyState === 4 && xhr.status === 200 && document.getElementById('text').value !== '') {
            var response = JSON.parse(xhr.responseText);

            var newMessage = document.createElement('div');
            newMessage.className = 'flex gap-2 flex-row-reverse items-end';
            newMessage.innerHTML = `
                <div class="px-4 py-2 rounded-[20px] max-w-sm bg-gradient-to-tr from-sky-500 to-blue-500 text-white shadow">
                    ${response.text}
                </div>
            `;

            document.getElementById('chat').appendChild(newMessage);
            document.getElementById('text').value = '';
            document.getElementById('file').value = '';
          } else {
            console.log('Произошла ошибка при отправке сообщения.');
          }
        };
        xhr.send(formData);
}