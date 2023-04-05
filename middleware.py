import wikipediaapi
import models

# Создание объекта для работы с Википедией
wiki = wikipediaapi.Wikipedia('ru')

def get_links(title):
    # Получаем страницу с заданным заголовком
    page = wiki.page(title)
    links = []
    if page.exists():
        # Получаем ссылки на другие статьи из данной страницы
        links = [link for link in page.links]
    return links

def shortest_path(start_title, end_title):
    # Создаем словарь, где ключи - это статьи, а значения - списки ссылок на другие статьи
    banwords = [i.word for i in models.BanWords.query.all()]
    links_dict = {}
    visited = set()
    queue = [[start_title]]

    while queue:
        path = queue.pop(0)
        node = path[-1]


        if node not in visited:
            links = get_links(node)
            links_dict[node] = links
                
            if end_title in links:
                return path + [end_title]

            for link in links:
                if link in banwords:
                    continue
                new_path = list(path)
                new_path.append(link)
                queue.append(new_path)

            visited.add(node)

    return None

