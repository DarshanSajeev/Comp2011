// Makes sure script only runs after everything is loaded
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".like-button").forEach(function(button) {
        // Checks for the button click
        button.addEventListener("click", function() {
            var postId = this.getAttribute("data-post-id");
            var likeCountElement = document.querySelector("#like-count-" + postId);

            // Send an AJAX request to the server
            fetch('/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ post_id: postId }),
            })
            // Parses the response
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    likeCountElement.textContent = data.likes;
                } else {
                    console.error(data.message);
                }
            })
            // Logs errors
            .catch(error => console.error('Error:', error));
        });
    });
});