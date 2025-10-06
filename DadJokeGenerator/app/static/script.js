document.addEventListener('DOMContentLoaded', () => {
    const jokeBtn = document.getElementById('jokeBtn');
    const jokeDisplay = document.getElementById('jokeDisplay');
    const jokeSound = document.getElementById('jokeSound');

    jokeBtn.addEventListener('click', () => {
        fetchJoke();
        jokeSound.play();
    });

    function fetchJoke() {
        fetch('/api-key')
            .then(response => response.json())
            .then(data => {
                const apiKey = data.apiKey;
                return fetch('https://api.api-ninjas.com/v1/dadjokes', {
                    headers: {
                        'Accept': 'application/json',
                        'X-Api-Key': apiKey
                    }
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    jokeDisplay.textContent = data[0].joke;
                } else {
                    jokeDisplay.textContent = 'No jokes found.';
                }
            })
            .catch(error => {
                jokeDisplay.textContent = 'Oops! Something went wrong. Please try again.';
                console.error('Error fetching joke:', error);
            });
    }
});