// frontend/src/store/gameSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// === TYPES ===
export interface PlayerStats {
  strength: { base: number; modifier: number };
  agility: { base: number; modifier: number };
  intelligence: { base: number; modifier: number };
  spirit: { base: number; modifier: number };
  vitality: { base: number; modifier: number };
}

export interface PlayerState {
  vkId: number | null;
  username: string;
  avatar: string;
  characterClass: string;
  level: number;
  experience: number;
  gold: number;
  location: string;
  hp: number;
  maxHp: number;
  mana: number;
  maxMana: number;
  stamina: number;
  maxStamina: number;
  fatigueState: string;
  inCombat: boolean;
  stats: PlayerStats;
}

export interface InventoryState {
  items: Array<{
    id: number;
    name: string;
    type: string;
    rarity: string;
    quantity: number;
    equipped: boolean;
  }>;
  equipment: Record<string, number | null>;
  slots: { used: number; max: number };
  gold: number;
}

export interface CombatState {
  active: boolean;
  combatId: number | null;
  opponent: {
    name: string;
    hp: number;
    maxHp: number;
    avatar?: string;
  } | null;
  log: Array<{
    timestamp: string;
    message: string;
    type: 'info' | 'damage' | 'heal' | 'system';
  }>;
  turn: number;
  playerTurn: boolean;
}

export interface UIState {
  loading: boolean;
  error: string | null;
  notifications: Array<{
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
  }>;
  activeModal: string | null;
  vkBridgeReady: boolean;
}

// === INITIAL STATE ===
const initialPlayerState: PlayerState = {
  vkId: null,
  username: 'Игрок',
  avatar: '',
  characterClass: 'warrior',
  level: 1,
  experience: 0,
  gold: 0,
  location: 'village',
  hp: 150,
  maxHp: 150,
  mana: 50,
  maxMana: 50,
  stamina: 150,
  maxStamina: 150,
  fatigueState: 'fit',
  inCombat: false,
  stats: {
    strength: { base: 10, modifier: 0 },
    agility: { base: 10, modifier: 0 },
    intelligence: { base: 10, modifier: 0 },
    spirit: { base: 10, modifier: 0 },
    vitality: { base: 10, modifier: 0 },
  },
};

const initialInventoryState: InventoryState = {
  items: [],
  equipment: {
    main_hand: null,
    off_hand: null,
    head: null,
    chest: null,
    legs: null,
    feet: null,
    hands: null,
    neck: null,
    ring: null,
    trinket: null,
  },
  slots: { used: 0, max: 20 },
  gold: 0,
};

const initialCombatState: CombatState = {
  active: false,
  combatId: null,
  opponent: null,
  log: [],
  turn: 1,
  playerTurn: true,
};

const initialUIState: UIState = {
  loading: false,
  error: null,
  notifications: [],
  activeModal: null,
  vkBridgeReady: false,
};

// === SLICE ===
const gameSlice = createSlice({
  name: 'game',
  initialState: {
    player: initialPlayerState,
    inventory: initialInventoryState,
    combat: initialCombatState,
    ui: initialUIState,
  },
  reducers: {
    // Player actions
    setPlayerData: (state, action: PayloadAction<Partial<PlayerState>>) => {
      state.player = { ...state.player, ...action.payload };
    },
    updatePlayerStats: (state, action: PayloadAction<PlayerStats>) => {
      state.player.stats = action.payload;
    },
    updateResources: (state, action: PayloadAction<{
      hp?: number;
      mana?: number;
      stamina?: number;
      gold?: number;
      experience?: number;
    }>) => {
      const { hp, mana, stamina, gold, experience } = action.payload;
      if (hp !== undefined) state.player.hp = hp;
      if (mana !== undefined) state.player.mana = mana;
      if (stamina !== undefined) state.player.stamina = stamina;
      if (gold !== undefined) state.player.gold = gold;
      if (experience !== undefined) state.player.experience = experience;
    },
    setLocation: (state, action: PayloadAction<string>) => {
      state.player.location = action.payload;
    },
    setInCombat: (state, action: PayloadAction<boolean>) => {
      state.player.inCombat = action.payload;
    },

    // Inventory actions
    setInventory: (state, action: PayloadAction<InventoryState>) => {
      state.inventory = action.payload;
    },
    addItem: (state, action: PayloadAction<{
      id: number;
      name: string;
      type: string;
      rarity: string;
      quantity?: number;
    }>) => {
      const existing = state.inventory.items.find(i => i.id === action.payload.id);
      if (existing) {
        existing.quantity += action.payload.quantity ?? 1;
      } else {
        state.inventory.items.push({
          ...action.payload,
          quantity: action.payload.quantity ?? 1,
          equipped: false,
        });
      }
      state.inventory.slots.used += 1;
    },
    removeItem: (state, action: PayloadAction<{ id: number; quantity?: number }>) => {
      const index = state.inventory.items.findIndex(i => i.id === action.payload.id);
      if (index !== -1) {
        const item = state.inventory.items[index];
        const qty = action.payload.quantity ?? item.quantity;
        if (qty >= item.quantity) {
          state.inventory.items.splice(index, 1);
          state.inventory.slots.used -= 1;
        } else {
          item.quantity -= qty;
        }
      }
    },
    equipItem: (state, action: PayloadAction<{ itemId: number; slot: string }>) => {
      const { itemId, slot } = action.payload;
      // Unequip current item in slot
      const currentEquipped = state.inventory.equipment[slot];
      if (currentEquipped) {
        const item = state.inventory.items.find(i => i.id === currentEquipped);
        if (item) item.equipped = false;
      }
      // Equip new item
      state.inventory.equipment[slot] = itemId;
      const item = state.inventory.items.find(i => i.id === itemId);
      if (item) item.equipped = true;
    },

    // Combat actions
    startCombat: (state, action: PayloadAction<{
      combatId: number;
      opponent: { name: string; hp: number; maxHp: number; avatar?: string };
    }>) => {
      state.combat.active = true;
      state.combat.combatId = action.payload.combatId;
      state.combat.opponent = action.payload.opponent;
      state.combat.log = [];
      state.combat.turn = 1;
      state.combat.playerTurn = true;
      state.player.inCombat = true;
    },
    endCombat: (state, action: PayloadAction<{
      winner: 'player' | 'opponent' | 'draw';
      rewards?: { gold?: number; exp?: number; items?: number[] };
    }>) => {
      state.combat.active = false;
      state.combat.combatId = null;
      state.combat.opponent = null;
      state.player.inCombat = false;
      if (action.payload.rewards) {
        if (action.payload.rewards.gold) {
          state.player.gold += action.payload.rewards.gold;
        }
        if (action.payload.rewards.exp) {
          state.player.experience += action.payload.rewards.exp;
        }
      }
    },
    addCombatLog: (state, action: PayloadAction<{
      message: string;
      type: 'info' | 'damage' | 'heal' | 'system';
    }>) => {
      state.combat.log.push({
        timestamp: new Date().toISOString(),
        ...action.payload,
      });
    },
    setCombatTurn: (state, action: PayloadAction<{
      turn: number;
      playerTurn: boolean;
      opponentHp?: number;
      playerHp?: number;
    }>) => {
      state.combat.turn = action.payload.turn;
      state.combat.playerTurn = action.payload.playerTurn;
      if (action.payload.opponentHp && state.combat.opponent) {
        state.combat.opponent.hp = action.payload.opponentHp;
      }
      if (action.payload.playerHp) {
        state.player.hp = action.payload.playerHp;
      }
    },

    // UI actions
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.ui.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.ui.error = action.payload;
    },
    addNotification: (state, action: PayloadAction<{
      message: string;
      type: 'success' | 'error' | 'warning' | 'info';
      duration?: number;
    }>) => {
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 5);
      state.ui.notifications.push({
        id,
        ...action.payload,
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.ui.notifications = state.ui.notifications.filter(
        n => n.id !== action.payload
      );
    },
    setModal: (state, action: PayloadAction<string | null>) => {
      state.ui.activeModal = action.payload;
    },
    setVkBridgeReady: (state, action: PayloadAction<boolean>) => {
      state.ui.vkBridgeReady = action.payload;
    },

    // Reset actions
    resetGame: () => ({
      player: initialPlayerState,
      inventory: initialInventoryState,
      combat: initialCombatState,
      ui: initialUIState,
    }),
  },
});

export const {
  setPlayerData,
  updatePlayerStats,
  updateResources,
  setLocation,
  setInCombat,
  setInventory,
  addItem,
  removeItem,
  equipItem,
  startCombat,
  endCombat,
  addCombatLog,
  setCombatTurn,
  setLoading,
  setError,
  addNotification,
  removeNotification,
  setModal,
  setVkBridgeReady,
  resetGame,
} = gameSlice.actions;

export default gameSlice.reducer;