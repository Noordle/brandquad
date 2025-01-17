#Django приложение для обработки и агрегации Apache лога.
В составе приложения должна быть `Management command`, которая на вход принимает ссылку на лог файл определенного формата, скачивает ее, парсит и записывает в БД. 

Ссылка для теста:
`http://www.almhuette-raith.at/apache-log/access.log (размер файла 186 Мб)`

### Поля модели должны содержать минимум: 
1) IP адрес; 
2) Дата из лога; 
3) http метод (GET, POST,...); 
4) URI запроса; 
5) Код ошибки; 
6) Размер ответа.
7) Другие данные из лога - опциональны.

В `django admin` необходимо реализовать вывод данных, описанных в модели, с пагинацией и поиском._

### Статистика должна содержать следующие данные:
1) Количество уникальных IP;
2) Top 10 самых распространенных IP адресов, в формате таблички где указан IP адрес и количество его вхождений
3) Количество GET, POST, ... (http методов)
4) Общее кол-во переданных байт (суммарное значение по полю "размер ответа")

Учесть, что эти агрегированные данные должны меняться при использовании поиска.

### Плюсами будут:

1) Хорошее оформление и комментирование кода (не излишнее, но хорошее);
2) Упаковка проекта в docker/docker-compose;
3) Оптимизация запросов к БД;
4) Кнопка экспорта данных на таблице с результатами, при нажатии на которую будет скачиваться файлик в формате XLSX с результатами выдачи;

Деплой:
1) Создать и заполнить файл `.envs`
2) `docker-compose -f docker-compose.yml up --build -d`
3) http://0.0.0.0:8000/admin
4) Пароль и логин администратора в `.envs` файле
