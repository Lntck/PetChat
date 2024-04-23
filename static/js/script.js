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
    xhr.onreadystatechange = function () {
        console.log(xhr.readyState)
        console.log(xhr.status)
        if (xhr.readyState === 4 && xhr.status === 200 && document.getElementById('text').value !== '') {
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


function searchUser() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/users_search/' + document.getElementById("search_input").value, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200 && JSON.parse(xhr.responseText).text !== "") {
            let usersData = JSON.parse(xhr.responseText);
            let searchList = document.getElementById('search_list');
            usersData.forEach(user => {
                let userElement = document.createElement('a');
                userElement.href = `/profile/${user.id}`;
                userElement.className = 'relative flex items-center gap-3 p-2 duration-200 rounded-xl hover:bg-secondery';

                userElement.innerHTML = `
                            <img src="/static/images/avatars/${user.avatar}" alt="" class="bg-gray-200 rounded-full w-10 h-10">
                            <div class="flex-1 min-w-0">
                                <h4 class="font-medium text-sm text-black dark:text-white">${user.name}</h4>
                            </div>
                            <a href="/message/${user.id}">
                                <button type="submit" class="text-sm rounded-full py-1.5 px-4 font-semibold bg-secondery">Написать</button>
                            </a>
                        `;

                searchList.appendChild(userElement);
            });
        }
    };
    xhr.send();
}


function scrollToBottom() {
    var chatContainer = document.getElementById('chat1');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

scrollToBottom();


var textarea = document.querySelector('textarea');
textarea.addEventListener('input', autoResize, false);

function autoResize() {

    this.style.height = 'auto';

    this.style.height = this.scrollHeight + 'px';

}