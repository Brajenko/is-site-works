import logging
import json
import asyncio
import pathlib

from nicegui import app, ui, Client
from nicegui.page import page
import validators
import config
from notifications.tgbot import send_message, check_id, get_link

try:
    from comparer.scheduler import MyScheduler
    from db.utils import *
    from db.schemas import *
    
    scheduler = MyScheduler()
    for tr in get_all_trackings():
        scheduler.add_tracking(tr)
except Exception:
    pass

logging.basicConfig(level=logging.INFO)


not_blank = {
    'Поле не может быть пустым': lambda x: x is not None and x != '',
}



@app.exception_handler(500)
async def exception_handler_500(request, exception: Exception):
    with Client(page('')) as client:
        ui.markdown('# Приложение не настроено или настроено некорректно. Перейдите в [настройки](/settings)')
    return client.build_response(request, 500)


@ui.page('/')
def index():
    def delete_tracking(event):
        tr_id = event.args
        scheduler.remove_tracking_by_id(tr_id)
        delete_tracking_by_id(tr_id)
        trackings_list_ui.refresh()

    @ui.refreshable
    def create_new_tracking_ui():
        url_input = ui.input(
            'Ссылка на сайт',
            placeholder='https://www.example.com',
            validation={
                **not_blank,
                'Ссылка должна быть в правильном формате': lambda x: validators.url(
                    x
                )
                == True,
            },
        ).style('width: 50%')
        with ui.row().style('width: 50%; gap: 5%;'):
            minutes_input = ui.number(
                'Интервал в минутах',
                placeholder='10',
                validation={
                    **not_blank,
                    'Количество минут должно быть ≥ 0': lambda x: int(x) >= 0,
                },
            ).style('width: 45%')
            seconds_input = ui.number(
                'Интервал в секундах',
                placeholder='30',
                validation={
                    **not_blank,
                    'Количество секунд должно быть ≥ 0': lambda x: int(x) >= 0,
                    'Интервал должен быть > 0': lambda x: minutes_input.value
                    or x,
                },
            ).style('width: 45%')
        save_all_screenshots_input = ui.checkbox(
            'Сохранять все скриншоты', value=False
        )

        def add_new_tracking():
            if not all(
                [
                    field.validate()
                    for field in [minutes_input, seconds_input, url_input]
                ]
            ):
                ui.notification(
                    'Исправьте все неправильно заполненные поля!',
                    color='negative',
                )
                return
            if not minutes_input.value and not seconds_input.value:
                print(minutes_input.value, seconds_input.value)
                seconds_input.error = 'Интервал должен быть больше 0'
                ui.notification(
                    'Исправьте все неправильно заполненные поля!',
                    color='negative',
                )
                return
            tr = create_new_tracking(
                TrackingCreateSchema(
                    url=url_input.value,
                    interval=dt.timedelta(
                        minutes=int(minutes_input.value),
                        seconds=int(seconds_input.value),
                    ),
                    save_all_screenshots=save_all_screenshots_input.value,
                )
            )
            # add new tracking
            trackings_list_ui.refresh()
            # clear fields
            create_new_tracking_ui.refresh()

            scheduler.add_tracking(tr)

        ui.button(
            'Добавить',
            on_click=add_new_tracking,
        )

    @ui.refreshable
    def trackings_list_ui():
        trackings = get_all_trackings()
        table = ui.table(
            columns=[
                {
                    'name': 'url',
                    'label': 'Ссылка',
                    'field': 'url',
                    'required': True,
                },
                {
                    'name': 'interval',
                    'label': 'Интервал',
                    'field': 'interval',
                    'required': True,
                },
                {
                    'name': 'last_state',
                    'label': 'Последнее состояние',
                    'field': 'last_state',
                    'required': True,
                },
            ],
            rows=[
                {
                    'id': tr.id,
                    'url': str(tr.url),
                    'interval': str(tr.interval),
                    'last_state': (
                        '/screenshots/'
                        + tr.last_state.image_filename.split(config.screenshots_folder)[
                            1
                        ]
                        if tr.last_state
                        else 'none'
                    ),
                }
                for tr in trackings
            ],
            row_key='user',
        )
        table.add_slot(
            'header',
            r"""
        <q-tr :props="props">
            <q-th auto-width />
            <q-th v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.label }}
            </q-th>
        </q-tr>
        """,
        )
        table.add_slot(
            'body',
            r"""
        <q-tr :props="props">
            <q-td auto-width>
                <q-btn size="sm" color="negative" round dense
                    @click="$parent.$emit('deleteTracking', props.row.id); console.log(123)"
                    icon="remove" />
            </q-td>
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
                <a v-if="col.field == 'last_state' || col.field == 'url'" :href="col.value">{{ col.value }}</a>
                <p v-else>{{ col.value }}</p>
            </q-td>
        </q-tr>
    """,
        )
        table.add_slot(
            'body-cell-url',
            r"""
            <q-td :props="props">
                <a :href="props.value">{{ props.value }}</a>
            </q-td>
        """,
        )
        table.add_slot(
            'body-cell-last_state',
            r"""
            <q-td :props="props">
                <a :href="props.value">{{ props.value }}</a>
            </q-td>
        """,
        )
        table.on('deleteTracking', delete_tracking)

    app.add_static_files('/screenshots', config.screenshots_folder)
    ui.page_title('Главная | Is Site Works')
    ui.markdown('## Добавить новый сайт в отслеживание')
    create_new_tracking_ui()
    ui.markdown('## Все отслеживания')
    trackings_list_ui()
    ui.timer(3.0, lambda: trackings_list_ui.refresh())
    ui.colors(
        primary=config.primary_color,
        positive=config.positive_color,
        negative=config.negative_color,
    )


@ui.page('/settings')
def settings():
    async def save():
        if tg_user_tg_id_input.value != config.tg_user_tg_id:
            try:
                await check_id(
                    tg_user_tg_id_input.value,
                    'Настройки изменены. Перезапустите приложение.',
                )
            except ValueError:
                ui.notification(
                    f'Бот не может отправить вам сообщение. Вы должны начать диалог с ним. {get_link()}',
                    color='negative',
                )
        data = {
            'tg': {
                'user_tg_id': tg_user_tg_id_input.value,
                'tg_bot_token': tg_bot_token_input.value,
            },
            'gui': {
                'primary_color': primary_color_input.value,
                'positive_color': positive_color_input.value,
                'negative_color': negative_color_input.value,
            },
            'mysql': {
                'name': mysql_name_input.value,
                'username': mysql_username_input.value,
                'password': mysql_password_input.value,
                'hostname': mysql_hostname_input.value,
                'port': str(mysql_port_input.value),
            },
            'screenshots': {
                'folder': screenshots_folder_input.value,
            },
        }
        with open('./settings.json', mode='w') as file:
            json.dump(data, file)
        ui.notification(
            'Настройки сохранены. Перезапустите приложение.', color='positive'
        )

    ui.page_title('Настройки | Is Site Works')
    ui.markdown('## Настройки')
    ui.markdown(
        f'Все настройки хранятся в файле [settings.json](file:/{str(pathlib.Path().resolve())}/settings.json) их можно редактировать и там'
    )
    ui.markdown('#### Telegram')
    with ui.row():
        tg_user_tg_id_input = ui.number(
            'ID пользователя в Telegram',
            placeholder='123456789',
            value=config.tg_user_tg_id,
        )
        tg_bot_token_input = ui.input(
            'Токен бота в Telegram',
            placeholder='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
            value=config.tg_bot_token,
            password=True,
            password_toggle_button=True,
        )
    ui.markdown('#### Интерфейс')
    primary_color_input = ui.color_input(
        'Основной цвет',
        placeholder='#FFFFFF',
        value=config.primary_color,
        preview=True,
    )
    positive_color_input = ui.color_input(
        'Положительный цвет',
        placeholder='#FFFFFF',
        value=config.positive_color,
        preview=True,
    )
    negative_color_input = ui.color_input(
        'Отрицательный цвет',
        placeholder='#FFFFFF',
        value=config.negative_color,
        preview=True,
    )
    ui.markdown('#### MySQL')
    with ui.row():
        mysql_name_input = ui.input(
            'Имя базы данных',
            placeholder='my_database',
            value=config.mysql_name,
        )
        mysql_hostname_input = ui.input(
            'Хост', placeholder='localhost', value=config.mysql_hostname
        )
        mysql_port_input = ui.number(
            'Порт', placeholder='3306', value=int(config.mysql_port)
        )
    with ui.row():
        mysql_username_input = ui.input(
            'Имя пользователя', placeholder='user', value=config.mysql_username
        )
        mysql_password_input = ui.input(
            'Пароль пользователя',
            placeholder='password',
            value=config.mysql_password,
            password=True,
            password_toggle_button=True,
        )
    ui.markdown('#### Скриншоты')
    screenshots_folder_input = ui.input(
        'Папка для скриншотов',
        placeholder='C:/screenshots',
        value=config.screenshots_folder,
    ).style('width: 100%;')
    ui.button('Сохранить', on_click=save)
    ui.colors(
        primary=config.primary_color,
        positive=config.positive_color,
        negative=config.negative_color,
    )

try:
    ui.run(reload=False)
except KeyboardInterrupt:
    print('Приложение завершает работу...')
