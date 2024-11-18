FETCH_TILES_EXAMPLE = \
"""
{
	"event": "fetch-tiles",
	"payload": {
		"start_x": 0,
		"start_y": 0,
		"end_x": 0,
		"end_y": 0
	}
}
"""

TILES_EXAMPLE = \
"""
{
	"event": "tiles",
	"payload": {
		"start_x": 0,
		"start_y": 0,
		"end_x": 4,
		"end_y": 4,
		"tiles": "CCCCCCCCCCC111CC1F1CC111C"
	}
}
"""

INVALID_EVENT_EXAMPLE = \
"""
{
	"event": "ayo invalid",
	"payload": {
		"foo": "bar"
	}
}
"""