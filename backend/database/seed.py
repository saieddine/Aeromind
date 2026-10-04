from .connection import SessionLocal
from .models import Aircraft, Component, Document


def seed_database():
    db = SessionLocal()

    try:
        aircraft = Aircraft(
            id="a320",
            manufacturer="Airbus",
            model="A320",
            description="Airbus A320 family narrow-body commercial aircraft."
        )

    # db.add(aircraft)
        document = Document(
            id="a320_ac_0624",
            aircraft_id="a320",
            title="Aircraft Characteristics – Airport and Maintenance Planning",
            file_path="data/documents/a320/AC_A320_0624.pdf",
            document_type="technical_manual"
     )

        db.add(document)

        components = [
            Component(
                id="engine_1",
                aircraft_id="a320",
                name="Engine 1",
                type="engine",
                description="Left-side aircraft engine."
            ),
            Component(
                id="engine_2",
                aircraft_id="a320",
                name="Engine 2",
                type="engine",
                description="Right-side aircraft engine."
            ),
            Component(
                id="left_wing",
                aircraft_id="a320",
                name="Left Wing",
                type="wing",
                description="Left wing of the aircraft."
            ),
            Component(
                id="right_wing",
                aircraft_id="a320",
                name="Right Wing",
                type="wing",
                description="Right wing of the aircraft."
            ),
            Component(
                id="fuselage",
                aircraft_id="a320",
                name="Fuselage",
                type="structure",
                description="Main body of the aircraft."
            ),
            Component(
                id="cockpit",
                aircraft_id="a320",
                name="Cockpit",
                type="flight_deck",
                description="Aircraft flight deck."
            ),
            Component(
                id="landing_gear",
                aircraft_id="a320",
                name="Landing Gear",
                type="landing_gear",
                description="Aircraft landing gear system."
            ),
            Component(
                id="tail",
                aircraft_id="a320",
                name="Tail",
                type="empennage",
                description="Aircraft tail assembly."
            )
        ]

        #db.add_all(components)
        db.commit()

        print("A320 seed data added successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()