from board import Point
from cursor.data import Cursor, Color


class CursorHandler:
    cursor_dict: dict[str, Cursor] = {}

    @staticmethod
    def create(conn_id: str):
        cursor = Cursor.create(conn_id)

        CursorHandler.cursor_dict[conn_id] = cursor

        return cursor

    @staticmethod
    def remove(conn_id: str):
        if conn_id in CursorHandler.cursor_dict:
            del CursorHandler.cursor_dict[conn_id]

    # range 안에 커서가 있는가
    @staticmethod
    def exists_range(start: Point, end: Point, *exclude_ids) -> list[Cursor]:
        result = []
        for key in CursorHandler.cursor_dict:
            if exclude_ids and key in exclude_ids:
                continue
            cur = CursorHandler.cursor_dict[key]
            if start.x > cur.position.x:
                continue
            if end.x < cur.position.x:
                continue
            if start.y < cur.position.y:
                continue
            if end.y > cur.position.y:
                continue
            result.append(cur)

        return result

    # 커서 view에 tile이 포함되는가
    @staticmethod
    def view_includes(p: Point, *exclude_ids) -> list[Cursor]:
        result = []
        for key in CursorHandler.cursor_dict:
            if exclude_ids and key in exclude_ids:
                continue
            cur = CursorHandler.cursor_dict[key]
            if (cur.position.x - cur.width) > p.x:
                continue
            if (cur.position.x + cur.width) < p.x:
                continue
            if (cur.position.y - cur.height) > p.y:
                continue
            if (cur.position.y + cur.height) < p.y:
                continue
            result.append(cur)

        return result
