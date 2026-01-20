from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.i18n import t
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from database.crud import *
from services.tmdb_api import get_content

router = Router()

def get_poster(content: dict):
    poster_path = content.get("poster_path")
    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoWcWg0E8pSjBNi0TtiZsqu8uD2PAr_K11DA&s"

    return poster

def get_data(content: dict, content_type: str, lang: str = "en-US"):
    overview = content.get("overview") or "Not available"
    rating = f'{round(content.get("vote_average", 0), 1)} / 10'

    match content_type:
        case "movie":
            media_type = 1
            genres = []
            title = content.get("title")
            release_str = content.get("release_date") or ""
            runtime = content.get("runtime") or 0
            year = release_str.split("-")[0] if release_str else None

            for i in content.get("genres"):
                genres.append(i.get("name"))

            caption = (
                f'🎬 {title}\n'
                f'{t("caption.runtime")} {runtime} {t("caption.minutes")}\n\n'
                f'{t("caption.release")} {year}\n'
                f'{t("caption.rating")} {rating}\n'
                f'{t("caption.genres")} {", ".join(genres)}\n\n'
                f'{t("caption.plot")} {overview}'
            )

        case "tv":
            media_type = 2
            genres = []
            title = content.get("name")
            release_str = content.get("first_air_date") or ""
            seasons = content.get("number_of_seasons") or 0
            episodes = content.get("number_of_episodes") or 0
            year = release_str.split("-")[0] if release_str else None

            for i in content.get("genres"):
                genres.append(i.get("name"))
                
            caption = (
                f'🎬 {title}\n'
                f'📺 {episodes} {t("caption.episodes")} {seasons} {t("caption.seasons")}\n\n'
                f'{t("caption.release")} {year}\n'
                f'{t("caption.rating")} {rating}\n'
                f'{t("caption.genres")} {", ".join(genres)}\n\n'
                f'{t("caption.plot")} {overview}'
            )

    return {
        "genres": genres,
        "title": title,
        "rating": rating,
        "caption": caption,
        "year": int(year),
        "media_type": media_type,
        "content_type": content_type
    }

def build_media_keyboard(items: list, content_id: str, content_type: str, limit: int = 10):
    builder = InlineKeyboardBuilder()

    for i in items[:limit]:
        match content_type:
            case "movie":
                title, release, cb_data = i.get("title"), i.get("release_date"), "movie_choice"
            case "tv":
                title, release, cb_data = i.get("name"), i.get("first_air_date"), "tv_choice"
            case _:
                continue
        adult = " 🔞" if i.get("adult") else ""
        year = release.split("-")[0] if release else "????"
        builder.button(text=f"{title}, {year}{adult}", callback_data=f"{cb_data}:{i.get('id')}")
    builder.attach(back_button(f"{content_type}_choice:{content_id}"))
    builder.adjust(1)
    return builder

@router.callback_query(SearchStates.waiting_for_choice, F.data.startswith(("movie", "tv")))
async def process_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    data = await state.get_data()
    parent = data.get("parent")
    content_id = callback.data.split(":", 1)[1]
    content_type = callback.data.split("_", 1)[0]

    lang = await get_locale(session, callback.message.chat.id)
    c_l, c_e = await get_content(content_type, content_id, lang), await get_content(content_type, content_id)
    c_l_data, c_e_data = get_data(c_l, content_type), get_data(c_e, content_type)
       
    await get_or_create_show(
        session=session,
        media_type=c_e_data.get("media_type"),
        tmdb_id=int(content_id),
        title=c_e_data.get("title"),
        genres=c_e_data.get("genres"),
        year=c_e_data.get("year"),
        poster=get_poster(c_e)
    )

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    c_obj = await session.scalar(select(Content).where(Content.tmdb_id == int(content_id)))

    res = await has_watched(session, user.id, c_obj.id)

    watched = t("watch_status.true") if res else t("watch_status.false")

    builder = InlineKeyboardBuilder()
    builder.button(text=watched, callback_data="add_confirm")
    builder.button(text=t("show_similar"), callback_data="find_similar")
    builder.button(text=t("main_menu"), callback_data="menu_delete")

    if parent in ("search", "trending"):
        builder.attach(back_button("go_back"))
    
    builder.adjust(1, 1, 2)

    await callback.message.answer_photo(
        photo=get_poster(c_l),
        caption=c_l_data.get("caption"),
        reply_markup=builder.as_markup())

    await callback.message.delete()

    await state.update_data(content=int(content_id))
    await state.update_data(content_type=c_e_data.get("content_type"))
    await state.set_state(SearchStates.waiting_for_confirmation)

@router.callback_query(SearchStates.waiting_for_confirmation)
async def confirm_content(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    
    data = await state.get_data()
    parent = data.get("parent")

    match callback.data:
        case "find_similar":
            await callback.answer()
            content_id = data.get("content")
            content_type = data.get("content_type")
            
            if not content_id:
                await callback.message.answer(t("state_empty"))
                return

            result = await get_content(content_type, content_id, "/similar")
            print(content_type, content_id)

            if result:
                builder = build_media_keyboard(result, content_id, content_type)

                logger.info(f"User {callback.message.chat.username} used /similar for movie {content_id}")

                await callback.message.answer(
                    t("choose.similar"),
                    reply_markup=builder.as_markup()
                )
                await callback.message.delete()

                await state.update_data(parent="similar")
                await state.set_state(SearchStates.waiting_for_choice)
            else:
                await callback.message.answer(t("no_similar"))
            
            return

        case "go_back":
            search_results = data.get("search_results", [])

            await callback.answer()

            if not search_results:
                await callback.answer(t("no_previous"))
                return

            builder = InlineKeyboardBuilder()

            for i in search_results[:10]:
                adult = " 🔞" if i.get("adult") else ""

                match i.get("media_type"):
                    case "movie":
                        title, release, media_type, c_data = i.get("title"), i.get("release_date"), t("type_movie"), "movie_choice"
                    case "tv":
                        title, release, media_type, c_data = i.get("name"), i.get("first_air_date"), t("type_tv"), "tv_choice"
                builder.button(text=f'{media_type} | {title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{c_data}:{i['id']}")
                
            builder.attach(back_button(parent))
            builder.adjust(1)

            await callback.message.answer(
                text=t("choose.content"), 
                reply_markup=builder.as_markup()
            )

            await callback.message.delete()

            await state.set_state(SearchStates.waiting_for_choice)

            return

        case "add_confirm":
            user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
            content = await session.scalar(select(Content).where(Content.tmdb_id == data.get("content")))
            result = await add_watched(session, user.id, content.id)

            watch_status = t("watch_status.true") if result else t("watch_status.false")
            watch_answer = t("collection.add") if result else t("collection.remove")

            await callback.answer(watch_answer)

            builder = InlineKeyboardBuilder()
            builder.button(text=watch_status, callback_data="add_confirm")
            builder.button(text=t("show_similar"), callback_data="find_similar")
            builder.button(text=t("main_menu"), callback_data="menu_delete")

            if parent in ("search", "trending"):
                builder.attach(back_button("go_back"))

            builder.adjust(1, 1, 2)

            logger.info(f"User {callback.message.chat.username} confirmed adding/removing content {content.tmdb_id}")

            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

            return