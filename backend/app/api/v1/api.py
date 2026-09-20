from fastapi import APIRouter

from app.api.v1.endpoints import admin, admin_logs, auth, categories, chat, comments, friend_links, messages, oauth, posts, reactions, rss, sitemap, site, stats, tags, tokens, track, upload

api_router = APIRouter()
api_router.include_router(site.router)
api_router.include_router(posts.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(admin.router)
api_router.include_router(admin_logs.router)
api_router.include_router(auth.router)
api_router.include_router(comments.router)
api_router.include_router(messages.router)
api_router.include_router(stats.router)
api_router.include_router(upload.router)
api_router.include_router(chat.router)
api_router.include_router(rss.router)
api_router.include_router(sitemap.router)
api_router.include_router(friend_links.router)
api_router.include_router(oauth.router)
api_router.include_router(reactions.router)
api_router.include_router(tokens.router)
api_router.include_router(track.router)
