from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.movie_states import MovieStates
from bot.keyboards.back_button import back_button
from database.crud import *
from datetime import datetime
from services.tmdb_api import get_movie_details, get_similar

router = Router()

@router.callback_query(MovieStates.waiting_for_choice, F.data.startswith(("choice:", "similar:")))
async def process_movie_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    data = await state.get_data()

    parent = data.get("parent")

    movie_id = callback.data.split(":", 1)[1]

    movie = await get_movie_details(movie_id)

    poster_path = movie.get("poster_path")
    if poster_path:
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
    else:
        poster = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoWcWg0E8pSjBNi0TtiZsqu8uD2PAr_K11DA&s"
        
    genres = []
    title = movie.get("original_title")
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

    await get_or_create_movie(
        session=session,
        tmdb_id=int(movie_id),
        title=title,
        rating=rating,
        genres=genres,
        year=year,
        duration=runtime,
        poster=poster
    )

    user_obj = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    movie_obj = await session.scalar(select(Movie).where(Movie.tmdb_id == int(movie_id)))

    res = await has_watched(
        session=session,
        user_id=user_obj.id,
        movie_id=movie_obj.id
    )

    watched = "✅ Watched - Click to change" if res else "❌ Not Watched - Click to change"

    builder = InlineKeyboardBuilder()
    builder.button(text=watched, callback_data="add_confirm")
    builder.button(text="Show Similar", callback_data="similar")
    builder.button(text="MAIN MENU", callback_data="menu_delete")

    if parent == "add_movie":
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
    await state.set_state(MovieStates.waiting_for_confirmation)

@router.callback_query(MovieStates.waiting_for_confirmation)
async def confirm_or_go_back(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    
    data = await state.get_data()
    parent = data.get("parent")

    if callback.data == "similar":
        await callback.answer()
        movie_id = data.get("movie")
        
        if not movie_id:
            await callback.message.answer("Movie ID missing, state is empty.")
            return

        result = await get_similar(movie_id)
        builder = InlineKeyboardBuilder()

        if result:
            for item in result:
                title = item.get("original_title")
                year = (item.get("release_date") or "").split("-")[0] or "????"
                adult = ", 18+" if item.get("adult") else ""

                builder.button(
                    text=f"{title}, {year}{adult}",
                    callback_data=f"similar:{item['id']}"
                )

            builder.adjust(1)

            await callback.message.answer(
                "Choose similar movie:",
                reply_markup=builder.as_markup()
            )

            await callback.message.delete()

            await state.set_state(MovieStates.waiting_for_choice)
        else:
            await callback.message.answer("No similar movies found.")
        
        return

    if callback.data == "go_back":
        search_results = data.get("search_results", [])

        await callback.answer()

        if not search_results:
            await callback.answer("There are no previous results")
            return

        builder = InlineKeyboardBuilder()
        for i in search_results:
            adult = ", 18+" if i.get("adult") else ""
            builder.button(text=f'{i.get("original_title")}, {i.get("release_date").split("-")[0] or "????"}{adult}',
                           callback_data=f"choice:{i['id']}")
        builder.attach(back_button("add_movie"))
        builder.adjust(1)

        await callback.message.answer(
            "Choose your movie:",
            reply_markup=builder.as_markup()
        )

        await callback.message.delete()

        await state.set_state(MovieStates.waiting_for_choice)

        return
    
    elif callback.data == "add_confirm":
        async with session.begin():
            user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
            movie = await session.scalar(select(Movie).where(Movie.tmdb_id == data.get("movie")))
            result = await add_movie_watched(session=session, user_id=user.id, movie_id=movie.id)

            if result:
                await callback.answer("Movie was added")

                builder = InlineKeyboardBuilder()
                builder.button(text="✅ Watched - Click to change", callback_data="add_confirm")
                builder.button(text="Show Similar", callback_data="similar")
                builder.button(text="MAIN MENU", callback_data="menu_delete")

                if parent == "add_movie":
                    builder.attach(back_button("go_back"))

                builder.adjust(1, 1, 2)

                await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
            else:
                await remove_movie_watched(session=session, user_id=user.id, movie_id=movie.id)

                await callback.answer("Movie was removed")

                builder = InlineKeyboardBuilder()
                builder.button(text="❌ Not Watched - Click to change", callback_data="add_confirm")
                builder.button(text="Show Similar", callback_data="similar")
                builder.button(text="MAIN MENU", callback_data="menu_delete")

                if parent == "add_movie":
                    builder.attach(back_button("go_back"))

                builder.adjust(1, 1, 2)

                await callback.message.edit_reply_markup(reply_markup=builder.as_markup())