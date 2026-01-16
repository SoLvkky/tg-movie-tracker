from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from database.crud import *
from datetime import datetime
from services.tmdb_api import get_movie_details, get_series_details, get_similar_movie, get_similar_series, search_content

router = Router()

@router.callback_query(SearchStates.waiting_for_choice, F.data.startswith(("movie_choice:", "movie_similar:")))
async def process_movie_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    data = await state.get_data()

    parent = data.get("parent")

    movie_id = callback.data.split(":", 1)[1]

    movie = await get_movie_details(movie_id)

    poster_path = movie.get("poster_path")
    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoWcWg0E8pSjBNi0TtiZsqu8uD2PAr_K11DA&s"
        
    genres = []
    title = movie.get("title")
    overview = movie.get("overview") or "Not available"
    rating = f'{round(movie.get("vote_average", 0), 1)} / 10'
    release_str = movie.get("release_date") or ""
    runtime = movie.get("runtime") or 0

    year = None
    if release_str:
        try:
            year = datetime.strptime(release_str, "%Y-%m-%d").year
        except ValueError:
            year = None

    for i in movie["genres"]:
        genres.append(i["name"])

    await get_or_create_show(
        session=session,
        media_type=1,
        tmdb_id=int(movie_id),
        title=title,
        genres=genres,
        year=year,
        poster=poster
    )

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    movie = await session.scalar(select(Content).where(Content.tmdb_id == int(movie_id)))

    res = await has_watched(
        session=session,
        user_id=user.id,
        content_id=movie.id
    )

    watched = "✅ Watched - Click to change" if res else "❌ Not Watched - Click to change"

    builder = InlineKeyboardBuilder()
    builder.button(text=watched, callback_data="add_movie_confirm")
    builder.button(text="Show Similar", callback_data="movie_similar")
    builder.button(text="MAIN MENU", callback_data="menu_delete")

    if parent == "search":
        builder.attach(back_button("go_back"))
    
    builder.adjust(1, 1, 2)

    await callback.message.answer_photo(photo=poster, caption=(
        f'🎬 {title}\n\n'
        f'🗓️ Release date: {year}\n'
        f'⭐ Rating: {rating}\n'
        f'🕒 Runtime: {runtime} minutes\n'
        f'🎭 Genres: {", ".join(genres)}\n\n'
        f'📜 Plot: {overview}'
    ), reply_markup=builder.as_markup())

    await callback.message.delete()

    await state.update_data(movie=int(movie_id))
    await state.set_state(SearchStates.waiting_for_movie_confirmation)

@router.callback_query(SearchStates.waiting_for_choice, F.data.startswith(("series_choice:", "series_similar:")))
async def process_series_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    data = await state.get_data()

    parent = data.get("parent")

    series_id = callback.data.split(":", 1)[1]

    series = await get_series_details(series_id)

    poster_path = series.get("poster_path")
    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoWcWg0E8pSjBNi0TtiZsqu8uD2PAr_K11DA&s"
        
    genres = []
    title = series.get("name")
    overview = series.get("overview") or "Not available"
    rating = f'{round(series.get("vote_average", 0), 1)} / 10'
    release_str = series.get("first_air_date") or ""
    seasons = series.get("number_of_seasons") or 0
    episodes = series.get("number_of_episodes") or 0

    year = None
    if release_str:
        try:
            year = datetime.strptime(release_str, "%Y-%m-%d").year
        except ValueError:
            year = None

    for i in series["genres"]:
        genres.append(i["name"])

    await get_or_create_show(
        session=session,
        media_type=2,
        tmdb_id=int(series_id),
        title=title,
        genres=genres,
        year=year,
        poster=poster
    )

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    series = await session.scalar(select(Content).where(Content.tmdb_id == int(series_id)))

    res = await has_watched(
        session=session,
        user_id=user.id,
        content_id=series.id
    )

    watched = "✅ Watched - Click to change" if res else "❌ Not Watched - Click to change"

    builder = InlineKeyboardBuilder()
    builder.button(text=watched, callback_data="add_series_confirm")
    builder.button(text="Show Similar", callback_data="series_similar")
    builder.button(text="MAIN MENU", callback_data="menu_delete")

    if parent == "search":
        builder.attach(back_button("go_back"))
    
    builder.adjust(1, 1, 2)

    await callback.message.answer_photo(photo=poster, caption=(
        f'🎬 {title}\n'
        f'📺 {episodes} episodes in {seasons} seasons\n\n'
        f'🗓️ Release date: {year}\n'
        f'⭐ Rating: {rating}\n'
        f'🎭 Genres: {", ".join(genres)}\n\n'
        f'📜 Plot: {overview}'
    ), reply_markup=builder.as_markup())

    await callback.message.delete()

    await state.update_data(series=int(series_id))
    await state.set_state(SearchStates.waiting_for_series_confirmation)

@router.callback_query(SearchStates.waiting_for_movie_confirmation)
async def confirm_movie(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    
    data = await state.get_data()
    parent = data.get("parent")

    if callback.data == "movie_similar":
        await callback.answer()
        movie_id = data.get("movie")
        
        if not movie_id:
            await callback.message.answer("Movie ID missing, state is empty.")
            return

        result = await get_similar_movie(movie_id)
        builder = InlineKeyboardBuilder()

        if result:
            for item in result[:5]:
                title = item.get("title")
                year = (item.get("release_date") or "").split("-")[0] or "????"
                adult = " 🔞" if item.get("adult") else ""

                builder.button(
                    text=f"{title}, {year}{adult}",
                    callback_data=f"movie_similar:{item['id']}"
                )

            builder.attach(back_button(f"movie_choice:{movie_id}"))
            builder.adjust(1)

            logger.info(f"User {callback.message.chat.username} used /movie_similar for movie {movie_id}")

            await callback.message.answer(
                "✨ Choose similar movie:",
                reply_markup=builder.as_markup()
            )

            await callback.message.delete()

            await state.update_data(parent="movie_similar")
            await state.set_state(SearchStates.waiting_for_choice)
        else:
            await callback.message.answer("No similar movies found.")
        
        return

    if callback.data == "go_back_movie":
        search_results = data.get("search_results", [])

        await callback.answer()

        if not search_results:
            await callback.answer("There are no previous results")
            return

        builder = InlineKeyboardBuilder()

        if search_results:
            for i in search_results[:5]:
                adult = " 🔞" if i.get("adult") else ""

                if i.get("media_type") == "movie":
                    title = i.get("title")
                    release = i.get("release_date")
                    media_type = "MOVIE"
                    callback = "movie_choice"

                elif i.get("media_type") == "tv":
                    title = i.get("name")
                    release = i.get("first_air_date")
                    media_type = "SERIES"
                    callback = "series_choice"

                builder.button(text=f'{media_type} | {title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{callback}:{i['id']}")
                
            builder.attach(back_button("search"))
            builder.adjust(1)

            await callback.answer("✨ Choose your movie/series:", reply_markup=builder.as_markup())
            await callback.message.delete()

            await state.set_state(SearchStates.waiting_for_choice)

            return
    
    if callback.data == "add_movie_confirm":

        await callback.answer("Movie was added")

        user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
        movie = await session.scalar(select(Content).where(Content.tmdb_id == data.get("movie")))
        result = await add_watched(session=session, user_id=user.id, movie_id=movie.id)

        watch_status = "✅ Watched - Click to change" if result else "❌ Not Watched - Click to change"

        builder = InlineKeyboardBuilder()
        builder.button(text=watch_status, callback_data="add_movie_confirm")
        builder.button(text="Show Similar", callback_data="movie_similar")
        builder.button(text="MAIN MENU", callback_data="menu_delete")

        if parent == "search_movie":
            builder.attach(back_button("go_back_movie"))

        builder.adjust(1, 1, 2)

        logger.info(f"User {callback.message.chat.username} confirmed adding/removing movie {movie.id}")

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

@router.callback_query(SearchStates.waiting_for_series_confirmation)
async def confirm_series(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    
    data = await state.get_data()
    parent = data.get("parent")

    if callback.data == "series_similar":
        await callback.answer()
        series_id = data.get("series")
        
        if not series_id:
            await callback.message.answer("Series ID missing, state is empty.")
            return

        result = await get_similar_series(series_id)
        builder = InlineKeyboardBuilder()

        if result:
            for item in result[:5]:
                title = item.get("name")
                year = (item.get("first_air_date") or "").split("-")[0] or "????"
                adult = " 🔞" if item.get("adult") else ""

                builder.button(
                    text=f"{title}, {year}{adult}",
                    callback_data=f"series_similar:{item['id']}"
                )

            builder.attach(back_button(f"series_choice:{series_id}"))
            builder.adjust(1)

            logger.info(f"User {callback.message.chat.username} used /series_similar for series {series_id}")

            await callback.message.answer(
                "✨ Choose similar series:",
                reply_markup=builder.as_markup()
            )

            await callback.message.delete()

            await state.update_data(parent="series_similar")
            await state.set_state(SearchStates.waiting_for_choice)
        else:
            await callback.message.answer("No similar series found.")
        
        return

    if callback.data == "go_back_series":
        search_results = data.get("search_results", [])

        await callback.answer()

        if not search_results:
            await callback.answer("There are no previous results")
            return

        builder = InlineKeyboardBuilder()

        if search_results:
            for i in search_results[:5]:
                adult = " 🔞" if i.get("adult") else ""

                if i.get("media_type") == "movie":
                    title = i.get("title")
                    release = i.get("release_date")
                    media_type = "MOVIE"
                    callback = "movie_choice"

                elif i.get("media_type") == "tv":
                    title = i.get("name")
                    release = i.get("first_air_date")
                    media_type = "SERIES"
                    callback = "series_choice"

                builder.button(text=f'{media_type} | {title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{callback}:{i['id']}")
                
            builder.attach(back_button("search"))
            builder.adjust(1)

            await callback.answer("✨ Choose your movie/series:", reply_markup=builder.as_markup())
            await callback.message.delete()

            await state.set_state(SearchStates.waiting_for_choice)

            return
    
    if callback.data == "add_series_confirm":
        await callback.answer()

        user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
        series = await session.scalar(select(Content).where(Content.tmdb_id == data.get("series")))
        result = await add_watched(session=session, user_id=user.id, content_id=series.id)

        watch_status = "✅ Watched - Click to change" if result else "❌ Not Watched - Click to change"

        builder = InlineKeyboardBuilder()
        builder.button(text=watch_status, callback_data="add_series_confirm")
        builder.button(text="Show Similar", callback_data="series_similar")
        builder.button(text="MAIN MENU", callback_data="menu_delete")

        if parent == "search":
            builder.attach(back_button("go_back_series"))

        builder.adjust(1, 1, 2)

        logger.info(f"User {callback.message.chat.username} confirmed adding/removing series {series.id}")

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())