"""Flask backend for the Blog API providing GET and POST endpoints for blog posts."""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Handle GET requests to retrieve all blog posts.

    Returns:
        Response: JSON list of all blog posts.
    """
    return jsonify(POSTS)


# Neue Route für POST /api/posts
@app.route('/api/posts', methods=['POST'])
def create_post():
    """Handle POST requests to create a new blog post.

    Expects JSON with 'title' and 'content' fields.

    Returns:
        Response: JSON of the created post with status 201 on success,
                  or error message with status 400 if data is missing.
    """
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Missing title or content'}), 400
    # new ID gen
    if POSTS:
        new_id = max(post['id'] for post in POSTS) + 1
    else:
        new_id = 1
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Handle DELETE requests to remove a blog post by its ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: JSON message confirming deletion with status 200 if found,
                  or error message with status 404 if not found.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post['id'] == post_id), None)
    if post_to_delete:
        POSTS = [post for post in POSTS if post['id'] != post_id]
        return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200
    else:
        return jsonify({'error': 'Post not found'}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
