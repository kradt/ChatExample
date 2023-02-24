# Приклад Асинхроного програмування на осонові чату який працює за TCP протоколом на основі сокетів




Процесс роботи чату полягає в перевіркі сокетів які мають файловий дескриптор на готовність до запису або читання.

У програмі є генератор `server` в якому створюється основний сокет який потім ми будемо використовувати для обробки підключень користувачів.
У Генераторі запускається безкінечний цикл в якому виконується блокуий метод прослухування сокету для перевірки можливих підключень.
Для того щоб ций метод не заблокував потік виконання перед його викликом ми повертаємо ознаку блокуючого метода, передаючи кортеж де перший елемент є текстовиим позначенням операції а другий сокетом який блокує потік виконання, При обробкі цього сокету нашим event loop, коли сокет буде готовим до читання виконання цього генератора продовжиться, він прослухає можливі підключення та додасть до обробки в список task завдання регістрації підключеного користувача

Генератор `registration_user_socket` повертає ознаку блокуючого методу та чекає поки сокет буде готовий до запису, коли він готовий записати в себе дані, генератор через сокет відправляє підключеному клієнту повідомлення в якому просить ввести своє ім'я, після чого повертає ознаку блокуючого метода чекаючи доки користувач введе своє ім'я. Коли користувач введе своє ім'я наш evenv loop додасть завдання на отримання імені користувача в список task. Після чого обробить це завдання продовживши потік виконання генератору `registration_user_socket` в якому до словаря connection_users додасця новий елемент в якому ключом буде сокет користувача, а значенням ім'я яке він ввів. Після цих операцій генератор добавить нове завдання на обробку event loop додавши до списку task генератор `send_history_to_user`.

Генератор `send_history_to_user` повертає ознаку блокуючого методу та чекає поки сокет буде готовий до запису, коли він буде готовий, використовуючи метод класу `withJson` `get_history_chat()` ми записуємо в сокет всю історію нашого чату яка насобиралась за час спілкування користувачів. Після всіх операцій генератор `send_history_to_user` додає нову задачу до списку `task` - генератор `сlient`

Генератор `client` запускає безкінечний цикл, в якому першим ділом передає ознаку блокуючого методу та чекає, доки сокет буде готовий до читання. Коли сокет готовий, ми отримуємо дані, які були передані цьому сокету, і записуємо їх в історію повідомлень. Якщо ці дані є, ми проходимося циклом по всім підключеним сокетам. Якщо це текущий сокет, ми пропускаємо, а якщо ні, повертаємо ознаку блокуючого методу, дочекавшись відправляємо користувачу отримане повідомлення. Якщо користувач відключився, ми викликаємо функцію `disconnect_user_socket`, яка видаляє його сокет зі списку підключених, видаляє задачу на читання повідомлень цим сокетом і закриваємо сокет.

Функція `event_loop` є обробником цього процесу. Вона запускає цикл, який працює до тих пір, доки є завдання або ознаки блокуючих функцій. Доки завдань немає, за допомогою методу `select` з бібліотеки `select` ми перевіряємо списки з сокетами на готовність до читання або запису.
Метод `select` повертає списки з об'єктами, які готові до читання, запису або в яких виникли певні помилки. Циклом ми проходимося по ним та додаємо їх до списку task з задачами. У наступному блоку через `try-except` ми беремо перший елемент списку `task` та продовжуємо виконання генератора функцією `next()`. Якщо ознака блокуючого методу "read", ми додаємо його до списку `to_read` так само з "write".

В точці входу в нашу програму ми додаємо перше завдання до списку task - генератор server, та запускаємо evenv_loop



_В даному прикладі використовується утиліта netcat для створення з'єднання по TCP або UDP протоколу._

https://user-images.githubusercontent.com/68617006/221180660-ab407ca2-14ea-4c09-9b5f-b2d56f6e9e3f.mov





