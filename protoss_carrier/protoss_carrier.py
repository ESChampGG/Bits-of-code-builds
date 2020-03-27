import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.constants import *


class CarrierBot(sc2.BotAI):
  def select_target(self):
    targets = self.enemy_structures
    if targets:
      return targets.random.position, True

    targets = self.enemy_units
    if targets:
      return targets.random.position, True

    if self.units and min([u.position.distance_to(self.enemy_start_locations[0]) for u in self.units]) < 5:
      return self.enemy_start_locations[0].position, False

    return self.mineral_field.random.position, False

  async def on_step(self, iteration):
    nexus = self.townhalls.random

    carriers = self.units(UnitTypeId.CARRIER)
    if carriers:
      target, target_is_enemy_unit = self.select_target()
      for carrier in carriers:
        if target_is_enemy_unit and (carrier.is_idle or carrier.is_moving):
          self.do(carrier.attack(target))
        elif carrier.is_idle:
            self.do(carrier.move(target))

    if not self.structures(PYLON) and self.already_pending(PYLON) == 0 and self.can_afford(PYLON):
      await self.build(PYLON, near=nexus.position.towards(self.game_info.map_center, 5))
    if not self.structures(GATEWAY) and self.already_pending(GATEWAY) == 0 and self.can_afford(GATEWAY):
      await self.build(GATEWAY, near=nexus.position.towards(self.game_info.map_center, 5))
    if not self.structures(CYBERNETICSCORE) and self.already_pending(CYBERNETICSCORE) == 0 and self.can_afford(CYBERNETICSCORE):
      await self.build(CYBERNETICSCORE, near=nexus.position.towards(self.game_info.map_center, 5))
    if not self.structures(STARGATE) and self.already_pending(STARGATE) == 0 and self.can_afford(STARGATE):
      await self.build(STARGATE, near=nexus.position.towards(self.game_info.map_center, 5))
    if not self.structures(FLEETBEACON) and self.already_pending(FLEETBEACON) == 0 and self.can_afford(FLEETBEACON):
      await self.build(FLEETBEACON, near=nexus.position.towards(self.game_info.map_center, 5))
    if not self.gas_buildings and self.can_afford(ASSIMILATOR) and self.already_pending(ASSIMILATOR) == 0:
      vgs = self.vespene_geyser.closer_than(15, nexus)
      for vg in vgs:
        worker = self.select_build_worker(vg.position)
        if worker is None:
          break
        self.do(worker.build(ASSIMILATOR, vg))

    if self.supply_left < 10 and self.already_pending(PYLON) == 0 and self.can_afford(PYLON):
      await self.build(PYLON, near=nexus.position.towards(self.game_info.map_center, 5))

    for a in self.gas_buildings:
      if a.assigned_harvesters < a.ideal_harvesters:
        w = self.workers.closer_than(20, a)
        if w:
          self.do(w.random.gather(a))

    for scv in self.workers.idle:
      self.do(scv.gather(self.mineral_field.closest_to(nexus)))
        
    if self.can_afford(CARRIER):
      stargate = self.structures(STARGATE).random
      self.do(stargate.train(CARRIER))


def main():
  sc2.run_game(
    sc2.maps.get("(2)CatalystLE"),
    [Bot(Race.Protoss, CarrierBot(), name="Carrie"),
     Computer(Race.Random, Difficulty.VeryEasy)],
    realtime=False,
  )


if __name__ == "__main__":
    main()
