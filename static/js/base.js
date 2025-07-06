// Sample pins data
// const pins = [
//     {
//         image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
//         title: 'Beautiful Mountain',
//         user: { avatar: 'https://i.pravatar.cc/32?img=2', name: 'Alice' },
//         likes: 12,
//         liked: false,
//         saved: false
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80',
//         title: 'City Lights at Night',
//         user: { avatar: 'https://i.pravatar.cc/32?img=3', name: 'Bob' },
//         likes: 8,
//         liked: true,
//         saved: true
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=400&q=80',
//         title: 'Forest Path',
//         user: { avatar: 'https://i.pravatar.cc/32?img=4', name: 'Charlie' },
//         likes: 15,
//         liked: false,
//         saved: false
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=400&q=80',
//         title: 'Ocean Waves',
//         user: { avatar: 'https://i.pravatar.cc/32?img=5', name: 'Diana' },
//         likes: 23,
//         liked: true,
//         saved: false
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=400&q=80',
//         title: 'Sunset Beach',
//         user: { avatar: 'https://i.pravatar.cc/32?img=6', name: 'Eve' },
//         likes: 31,
//         liked: false,
//         saved: true
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=400&q=80',
//         title: 'Mountain Lake',
//         user: { avatar: 'https://i.pravatar.cc/32?img=7', name: 'Frank' },
//         likes: 19,
//         liked: true,
//         saved: false
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=400&q=80',
//         title: 'Autumn Trees',
//         user: { avatar: 'https://i.pravatar.cc/32?img=8', name: 'Grace' },
//         likes: 27,
//         liked: false,
//         saved: true
//     },
//     {
//         image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
//         title: 'Snowy Peaks',
//         user: { avatar: 'https://i.pravatar.cc/32?img=9', name: 'Henry' },
//         likes: 14,
//         liked: true,
//         saved: false
//     }
// ];

let pins = {{featured_pins|safe}};

// Render pins
function renderPins(pinList, containerId = 'pin-masonry') {
    const masonry = document.getElementById(containerId);
    if (!masonry) return;

    pinList.forEach((pin, idx) => {
        const card = document.createElement('div');
        card.className = 'pin-card';
        card.innerHTML = `
        <a href="pin-detail.html" class="text-decoration-none">
          <img src="${pin.image}" class="pin-img" alt="Pin image">
          <div class="p-3">
            <div class="pin-title" title="${pin.title}">${pin.title}</div>
            <div class="d-flex justify-content-between align-items-center mt-2">
              <div class="pin-user">
                <img src="${pin.user.avatar}" alt="User">
                <span class="text-muted small">${pin.user.name}</span>
              </div>
              <div class="pin-actions">
                <button class="btn btn-light btn-sm save-btn ${pin.saved ? 'text-danger' : ''}" title="Save" onclick="event.preventDefault(); event.stopPropagation();">
                  <i class="fas fa-thumbtack"></i>
                </button>
                <button class="btn btn-light btn-sm like-btn ${pin.liked ? 'liked' : ''}" title="Like" onclick="event.preventDefault(); event.stopPropagation();">
                  <i class="fas fa-heart"></i> <span class="like-count">${pin.likes}</span>
                </button>
              </div>
            </div>
          </div>
        </a>
      `;
        masonry.appendChild(card);
    });
}

// Infinite scroll placeholder
let loading = false;
window.addEventListener('scroll', () => {
    if (loading) return;
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
        loading = true;
        document.getElementById('loading-indicator').style.display = 'block';
        setTimeout(() => {
            // Simulate loading more pins
            renderPins(pins);
            document.getElementById('loading-indicator').style.display = 'none';
            loading = false;
        }, 1200);
    }
});

// Like/Save button interactions
document.addEventListener('click', function (e) {
    if (e.target.closest('.like-btn')) {
        const btn = e.target.closest('.like-btn');
        btn.classList.toggle('liked');
        const countSpan = btn.querySelector('.like-count');
        let count = parseInt(countSpan.textContent, 10);
        if (btn.classList.contains('liked')) {
            countSpan.textContent = count + 1;
        } else {
            countSpan.textContent = count - 1;
        }
    }
    if (e.target.closest('.save-btn')) {
        const btn = e.target.closest('.save-btn');
        btn.classList.toggle('text-danger');
    }
});

// Pin creation modal image preview
document.getElementById('pinImage').addEventListener('change', function (e) {
    const file = e.target.files[0];
    const preview = document.getElementById('imagePreview');
    if (file) {
        const reader = new FileReader();
        reader.onload = function (evt) {
            preview.src = evt.target.result;
            preview.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    } else {
        preview.classList.add('d-none');
        preview.src = '';
    }
});

// Prevent form submission (demo only)
document.getElementById('createPinForm').addEventListener('submit', function (e) {
    e.preventDefault();
    alert('Pin saved! (Demo only)');
    document.getElementById('createPinForm').reset();
    document.getElementById('imagePreview').classList.add('d-none');
    const modal = bootstrap.Modal.getInstance(document.getElementById('createPinModal'));
    modal.hide();
});

// Initial render
renderPins(pins);
