"""Flask backend for the Blog API providing GET, POST, PUT, DELETE, and SEARCH endpoints for blog posts."""

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
    """Handle GET requests to retrieve all blog posts, with optional sorting.

    Query Parameters:
        sort (str, optional): Field to sort by. Allowed values: 'title', 'content'.
        direction (str, optional): Sort direction. Allowed values: 'asc', 'desc'. Default is 'asc'.
            If 'sort' is not provided, 'direction' is ignored.

    Behavior:
        - If neither 'sort' nor 'direction' is provided, returns posts in original order.
        - If only 'direction' is provided, returns posts in original order.
        - If 'sort' is provided:
            - If 'sort' not in ('title', 'content'), returns 400 with error.
            - If 'direction' not in ('asc', 'desc'), returns 400 with error.
            - Otherwise, returns posts sorted case-insensitive by the given field and direction.

    Returns:
        Response: JSON list of blog posts (possibly sorted), or error with status 400 for invalid parameters.
    """
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')
    # If neither 'sort' nor 'direction' is set, return original order
    if sort_field is None and 'direction' not in request.args:
        return jsonify(POSTS)
    # If sort_field is set, validate and sort
    if sort_field is not None:
        if sort_field not in ('title', 'content'):
            return jsonify({'error': 'Invalid sort field. Allowed: title, content'}), 400
        if direction.lower() not in ('asc', 'desc'):
            return jsonify({'error': 'Invalid direction. Allowed: asc, desc'}), 400
        reverse = direction.lower() == 'desc'
        result = sorted(POSTS, key=lambda p: p[sort_field].lower(), reverse=reverse)
        return jsonify(result), 200
    # If only direction is set, but not sort, ignore and return original order
    return jsonify(POSTS)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Search for blog posts by title or content substring (case-insensitive).

    Query Parameters:
        title (str, optional): Substring to search for in the post titles.
        content (str, optional): Substring to search for in the post contents.

    Returns:
        Response: JSON list of matching blog posts with status 200.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()
    if not title_query and not content_query:
        result = POSTS
    else:
        result = [
            post for post in POSTS
            if (title_query and title_query in post['title'].lower()) or
               (content_query and content_query in post['content'].lower())
        ]
    return jsonify(result), 200


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
    missing = [field for field in ('title', 'content') if not data or field not in data]
    if missing:
        return jsonify({'error': f"Missing fields: {missing}"}), 400
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


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a blog post by its ID with provided title and/or content.

    Args:
        post_id (int): The ID of the post to update.

    Returns:
        Response: JSON of the updated post with status 200 if successful,
                  or error message with status 404 if post not found.
    """
    data = request.get_json(silent=True) or {}
    post = next((post for post in POSTS if post['id'] == post_id), None)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']
    return jsonify(post), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Handle DELETE requests to remove a blog post by its ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: JSON message confirming deletion with status 200 if found,
                  or error message with status 404 if not found.
    """
    post_to_delete = next((post for post in POSTS if post['id'] == post_id), None)
    if not post_to_delete:
        return jsonify({'error': 'Post not found'}), 404
    POSTS.remove(post_to_delete)
    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)