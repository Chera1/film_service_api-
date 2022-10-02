import uuid

from http import HTTPStatus
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException

from services.film import FilmService, get_film_service
from models.film import BaseFilmApi, DetailFilmApi

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get('/search',
            response_model=list[BaseFilmApi],
            summary="Поиск по фильмам",
            description="Осуществляет нечеткий поиск по фильмам",
            )
async def films(sort: Union[str, None] = None,
                limit: Optional[int] = 50,
                page: Optional[int] = 1,
                query: Optional[str] = None,
                film_service: FilmService = Depends(get_film_service)) -> \
        Union[list[BaseFilmApi], None]:
    """
    Возвращает результаты поиска по названию фильма

    @param sort: имя поля по которому идет сортировка
    @param limit: количество записей на странице
    @param page: номер страницы
    @param query: поисковый запрос
    @param film_service:
    @return: Данные по фильмам
    """

    films, errors = await film_service.get_films(sort=sort,
                                                 limit=limit,
                                                 page=page,
                                                 query=query,
                                                 genre=None)

    if errors:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=errors)

    search_film_list = [
        BaseFilmApi(uuid=film['_source']['id'],
                    title=film['_source']['title'],
                    imdb_rating=film['_source']['imdb_rating']
                    )
        for film in films
    ]

    return search_film_list


@router.get('/same/{film_id}',
            response_model=list[BaseFilmApi],
            summary="Похожие фильмы",
            description="Похожие фильмы для заданного фильма",
            )
async def same_films(
        film_id: uuid.UUID,
        sort: Union[str, None] = None,
        limit: Optional[int] = 50,
        page: Optional[int] = 1,
        film_service: FilmService = Depends(get_film_service)
) -> Union[list[BaseFilmApi], None]:
    """
    Возвращает похожие фильмы для заданного фильма

    @param film_id: uuid фильма
    @param sort: имя поля по которому идет сортировка
    @param limit: количество записей на странице
    @param page: номер страницы
    @param genre: uuid-жанра для фильтрации
    @param film_service:
    @return: Данные по похожим фильмам
    """

    result = await film_service.get_same_films(
        film_id=film_id,
        sort=sort,
        limit=limit,
        page=page
    )

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not exist or not results')

    films, errors = result

    if errors:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=errors)

    same_film_list = [
        BaseFilmApi(uuid=film['_source']['id'],
                    title=film['_source']['title'],
                    imdb_rating=film['_source']['imdb_rating']
                    )
        for film in films
        if film['_source']['id'] != film_id
    ]

    return same_film_list

@router.get('/',
            response_model=list[BaseFilmApi],
            summary="Информация по нескольким фильмам",
            description="Краткая информация по нескольким фильмам",
            )
async def films(sort: Union[str, None] = None,
                limit: Optional[int] = 50,
                page: Optional[int] = 1,
                genre: Optional[uuid.UUID] = None,
                film_service: FilmService = Depends(get_film_service)) -> \
        Union[list[BaseFilmApi], None]:
    """
    Возвращает информацию по нескольким фильмам

    @param sort: имя поля по которому идет сортировка
    @param limit: количество записей на странице
    @param page: номер страницы
    @param genre: uuid-жанра для фильтрации
    @param film_service:
    @return: Данные по фильмам
    """

    films, errors = await film_service.get_films(sort=sort,
                                                 limit=limit,
                                                 page=page,
                                                 genre=genre)

    if errors:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=errors)

    non_detail_film_list = [
        BaseFilmApi(uuid=film['_source']['id'],
                    title=film['_source']['title'],
                    imdb_rating=film['_source']['imdb_rating']
                    )
        for film in films
    ]

    return non_detail_film_list


@router.get('/{film_id}',
            response_model=DetailFilmApi,
            summary="Информация по одному фильму",
            description="Детальная информация по отдельному фильму",
            )
async def film_details(film_id: uuid.UUID,
                       film_service: FilmService =
                       Depends(get_film_service)) -> DetailFilmApi:
    """
    Возвращает информацию по одному фильму
    """
    film = await film_service.get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    return DetailFilmApi(uuid=film.id,
                         title=film.title,
                         imdb_rating=film.imdb_rating,
                         description=film.description,
                         genre=film.genre,
                         actors=film.actors,
                         writers=film.writers,
                         director=film.director
                         )