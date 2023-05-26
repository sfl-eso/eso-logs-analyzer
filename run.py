from models import EncounterLog, AbilityUptime

#
# def match_cast_events(events: dict):
#     end_casts = {end_cast.id: end_cast for end_cast in events["END_CAST"]}
#     for begin_cast in tqdm(events["BEGIN_CAST"], desc="Matching cast events"):
#         if begin_cast.id in end_casts:
#             end_cast = end_casts[begin_cast.id]
#             begin_cast.end_cast = end_cast
#             end_cast.begin_cast = begin_cast
#
#     # matched_b = [cast for cast in events["BEGIN_CAST"] if cast.end_cast is not None]
#     # not_matched_b = [cast for cast in events["BEGIN_CAST"] if cast.end_cast is None]
#     # matched_e = [cast for cast in events["END_CAST"] if cast.begin_cast is not None]
#     # not_matched_e = [cast for cast in events["END_CAST"] if cast.begin_cast is None]
#     b_ids = set([cast.id for cast in events["BEGIN_CAST"]])
#     e_ids = set([cast.id for cast in events["END_CAST"]])
#     intersect = b_ids.intersection(e_ids)
#     diff = b_ids.difference(e_ids)
#     return
#     # print(f"{len(events['BEGIN_CAST'])} begin casts")
#     # print(f"{len(events['END_CAST'])} end casts")
#     # print(f"{len(matched)} begin casts matched to end_casts")
#     # print(f"{len(not_matched)} begin casts not matched to end_casts")
#     # for index, begin_cast in tqdm(enumerate(events["BEGIN_CAST"]), desc="Matching cast events"):
#     #     if begin_cast.id not in end_casts:
#     #         print(f"{begin_cast.id} not in end cast dict")
#
from querying import EventSpan


def main():
    """
    https://www.esologs.com/reports/C6GkAg9VKPvYHzrx/
    """
    log = EncounterLog.parse_log("data/markarth_vka.log", multiple=False)
    encounters = log.combat_encounters
    first = encounters[0]
    span = EventSpan(first, first.end_combat)

    print(f"Inspecting encounter {first}")
    for event in span:
        print(f"Event: {event}")

    # crusher = log.ability_info_by_name("Crusher")

    # for encounter in encounters:
    #     uptimes = AbilityUptime.create_for_encounter(crusher, encounter)


if __name__ == "__main__":
    main()
