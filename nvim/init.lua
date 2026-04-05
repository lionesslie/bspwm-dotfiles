-- ══════════════════════════════════════════════════════════════
--  init.lua — neovim config for bspwm-dotfiles rice
--  Theme  : Catppuccin Mocha
--  Font   : JetBrainsMono Nerd Font
--  Plugin : lazy.nvim (auto-bootstrapped)
-- ══════════════════════════════════════════════════════════════

-- ── Options ───────────────────────────────────────────────────
vim.g.mapleader      = " "
vim.g.maplocalleader = " "

local opt = vim.opt

opt.number         = true
opt.relativenumber = true
opt.cursorline     = true
opt.signcolumn     = "yes"
opt.scrolloff      = 8
opt.sidescrolloff  = 8

opt.tabstop        = 4
opt.shiftwidth     = 4
opt.expandtab      = true
opt.smartindent    = true

opt.wrap           = false
opt.termguicolors  = true
opt.showmode       = false
opt.pumheight      = 10
opt.cmdheight      = 1

opt.ignorecase     = true
opt.smartcase      = true
opt.hlsearch       = false
opt.incsearch      = true

opt.splitbelow     = true
opt.splitright     = true

opt.undofile       = true
opt.swapfile       = false
opt.backup         = false

opt.updatetime     = 250
opt.timeoutlen     = 400

opt.list           = true
opt.listchars      = { tab = "→ ", trail = "·", nbsp = "␣" }
opt.fillchars      = { eob = " " }

-- ── Bootstrap lazy.nvim ───────────────────────────────────────
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- ── Plugins ───────────────────────────────────────────────────
require("lazy").setup({

  -- ── Colorscheme: Catppuccin Mocha ─────────────────────────
  {
    "catppuccin/nvim",
    name     = "catppuccin",
    priority = 1000,
    opts = {
      flavour                = "mocha",
      transparent_background = true,
      term_colors            = true,
      integrations = {
        cmp        = true,
        gitsigns   = true,
        telescope  = { enabled = true },
        treesitter = true,
        mason      = true,
        which_key  = true,
      },
    },
    config = function(_, opts)
      require("catppuccin").setup(opts)
      vim.cmd.colorscheme("catppuccin")
    end,
  },

  -- ── Statusline: Lualine ───────────────────────────────────
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    opts = {
      options = {
        theme                = "catppuccin",
        globalstatus         = true,
        component_separators = { left = "", right = "" },
        section_separators   = { left = "", right = "" },
      },
      sections = {
        lualine_a = { { "mode", icon = "" } },
        lualine_b = { { "branch", icon = "" }, "diff", "diagnostics" },
        lualine_c = { { "filename", path = 1 } },
        lualine_x = { "encoding", "fileformat", "filetype" },
        lualine_y = { "progress" },
        lualine_z = { { "location", icon = "" } },
      },
    },
  },

  -- ── Bufferline ────────────────────────────────────────────
  {
    "akinsho/bufferline.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("bufferline").setup({
        options = {
          diagnostics             = "nvim_lsp",
          separator_style         = "slant",
          show_buffer_close_icons = true,
          show_close_icon         = false,
          always_show_bufferline  = false,
        },
      })
    end,
  },

  -- ── File tree: Neo-tree ───────────────────────────────────
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch       = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons",
      "MunifTanjim/nui.nvim",
    },
    keys = {
      { "<leader>e", "<cmd>Neotree toggle<cr>", desc = "File tree" },
    },
    opts = {
      window = { width = 28 },
      filesystem = {
        filtered_items = {
          visible         = false,
          hide_dotfiles   = false,
          hide_gitignored = false,
        },
      },
    },
  },

  -- ── Telescope ─────────────────────────────────────────────
  {
    "nvim-telescope/telescope.nvim",
    branch       = "0.1.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    },
    keys = {
      { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "Find files" },
      { "<leader>fg", "<cmd>Telescope live_grep<cr>",  desc = "Live grep" },
      { "<leader>fb", "<cmd>Telescope buffers<cr>",    desc = "Buffers" },
      { "<leader>fh", "<cmd>Telescope help_tags<cr>",  desc = "Help" },
      { "<leader>fr", "<cmd>Telescope oldfiles<cr>",   desc = "Recent files" },
    },
    config = function()
      local telescope = require("telescope")
      local actions   = require("telescope.actions")
      telescope.setup({
        defaults = {
          prompt_prefix   = "   ",
          selection_caret = "  ",
          mappings = {
            i = {
              ["<C-j>"] = actions.move_selection_next,
              ["<C-k>"] = actions.move_selection_previous,
              ["<esc>"] = actions.close,
            },
          },
        },
      })
      telescope.load_extension("fzf")
    end,
  },

  -- ── LSP (nvim 0.11+ native API) ───────────────────────────
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      { "mason-org/mason.nvim" },
      { "mason-org/mason-lspconfig.nvim" },
    },
    config = function()
      require("mason").setup({
        ui = {
          border = "rounded",
          icons  = {
            package_installed   = "✓",
            package_pending     = "➜",
            package_uninstalled = "✗",
          },
        },
      })

      require("mason-lspconfig").setup({
        ensure_installed = { "lua_ls", "clangd",},
        automatic_enable = true,
      })

      -- LSP keymaps: sunucu attach olunca ayarlanır
      vim.api.nvim_create_autocmd("LspAttach", {
        callback = function(ev)
          local bufnr = ev.buf
          local map = function(keys, func, desc)
            vim.keymap.set("n", keys, func, { buffer = bufnr, desc = "LSP: " .. desc })
          end
          map("gd",         vim.lsp.buf.definition,   "Go to definition")
          map("gD",         vim.lsp.buf.declaration,  "Go to declaration")
          map("gr",         vim.lsp.buf.references,   "References")
          map("K",          vim.lsp.buf.hover,         "Hover docs")
          map("<leader>rn", vim.lsp.buf.rename,        "Rename")
          map("<leader>ca", vim.lsp.buf.code_action,   "Code action")
          map("<leader>d",  vim.diagnostic.open_float, "Diagnostic float")
          map("[d",         vim.diagnostic.goto_prev,  "Prev diagnostic")
          map("]d",         vim.diagnostic.goto_next,  "Next diagnostic")
        end,
      })

      -- nvim-cmp capabilities tüm sunuculara uygula
      vim.lsp.config("*", {
        capabilities = require("cmp_nvim_lsp").default_capabilities(),
      })

      -- Diagnostic görünüm
      local signs = { Error = " ", Warn = " ", Hint = "󰌵 ", Info = " " }
      for type, icon in pairs(signs) do
        local hl = "DiagnosticSign" .. type
        vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
      end
      vim.diagnostic.config({
        virtual_text     = { prefix = "●" },
        update_in_insert = false,
        float            = { border = "rounded" },
      })
    end,
  },

  -- ── Autocompletion ────────────────────────────────────────
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
      "L3MON4D3/LuaSnip",
      "saadparwaiz1/cmp_luasnip",
      "rafamadriz/friendly-snippets",
    },
    config = function()
      local cmp     = require("cmp")
      local luasnip = require("luasnip")
      require("luasnip.loaders.from_vscode").lazy_load()

      cmp.setup({
        snippet = {
          expand = function(args) luasnip.lsp_expand(args.body) end,
        },
        window = {
          completion    = cmp.config.window.bordered(),
          documentation = cmp.config.window.bordered(),
        },
        mapping = cmp.mapping.preset.insert({
          ["<C-k>"]     = cmp.mapping.select_prev_item(),
          ["<C-j>"]     = cmp.mapping.select_next_item(),
          ["<C-b>"]     = cmp.mapping.scroll_docs(-4),
          ["<C-f>"]     = cmp.mapping.scroll_docs(4),
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<C-e>"]     = cmp.mapping.abort(),
          ["<CR>"]      = cmp.mapping.confirm({ select = true }),
          ["<Tab>"]     = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then luasnip.expand_or_jump()
            else fallback() end
          end, { "i", "s" }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "luasnip" },
          { name = "buffer" },
          { name = "path" },
        }),
        formatting = {
          format = function(entry, vim_item)
            local kind_icons = {
              Text = "", Method = "󰆧", Function = "󰊕", Constructor = "",
              Field = "󰇽", Variable = "󰂡", Class = "󰠱", Interface = "",
              Module = "", Property = "󰜢", Unit = "", Value = "󰎠",
              Enum = "", Keyword = "󰌋", Snippet = "", Color = "󰏘",
              File = "󰈙", Reference = "", Folder = "󰉋", EnumMember = "",
              Constant = "󰏿", Struct = "", Event = "", Operator = "󰆕",
              TypeParameter = "󰅲",
            }
            vim_item.kind = string.format("%s %s", kind_icons[vim_item.kind] or "", vim_item.kind)
            vim_item.menu = ({
              nvim_lsp = "[LSP]", luasnip = "[Snippet]",
              buffer   = "[Buffer]", path = "[Path]",
            })[entry.source.name]
            return vim_item
          end,
        },
      })
    end,
  },

  -- ── Autopairs ─────────────────────────────────────────────
  {
    "windwp/nvim-autopairs",
    event = "InsertEnter",
    config = function()
      require("nvim-autopairs").setup({ check_ts = true })
      require("cmp").event:on(
        "confirm_done",
        require("nvim-autopairs.completion.cmp").on_confirm_done()
      )
    end,
  },

  -- ── Git signs ─────────────────────────────────────────────
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts  = {
      signs = {
        add          = { text = "▎" },
        change       = { text = "▎" },
        delete       = { text = "" },
        topdelete    = { text = "" },
        changedelete = { text = "▎" },
      },
    },
  },

  -- ── Indent guides ─────────────────────────────────────────
  {
    "lukas-reineke/indent-blankline.nvim",
    main  = "ibl",
    event = { "BufReadPost", "BufNewFile" },
    opts  = {
      indent  = { char = "│" },
      scope   = { enabled = true },
      exclude = { filetypes = { "neo-tree", "lazy", "mason" } },
    },
  },

  -- ── Which-key ─────────────────────────────────────────────
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    opts  = {
      icons = { separator = "→" },
      win   = { border = "rounded" },
    },
  },

  -- ── Comment ───────────────────────────────────────────────
  {
    "numToStr/Comment.nvim",
    keys = { { "gc", mode = { "n", "v" } }, { "gb", mode = { "n", "v" } } },
    opts = {},
  },

  -- ── Surround ──────────────────────────────────────────────
  {
    "kylechui/nvim-surround",
    event   = "VeryLazy",
    version = "*",
    opts    = {},
  },

  -- ── Colorizer ─────────────────────────────────────────────
  {
    "NvChad/nvim-colorizer.lua",
    event = { "BufReadPre", "BufNewFile" },
    opts  = { user_default_options = { tailwind = true } },
  },

  -- ── Todo comments ─────────────────────────────────────────
  {
    "folke/todo-comments.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    event        = { "BufReadPost", "BufNewFile" },
    opts         = {},
  },

  -- ── Smooth scrolling ──────────────────────────────────────
  {
    "karb94/neoscroll.nvim",
    event = "VeryLazy",
    opts  = { mappings = { "<C-u>", "<C-d>", "<C-b>", "<C-f>" } },
  },

}, {
  ui = {
    border = "rounded",
    icons  = {
      cmd        = " ", config     = "",
      event      = "", ft         = " ",
      init       = " ", import     = " ",
      keys       = " ", lazy       = "󰒲 ",
      loaded     = "●", not_loaded = "○",
      plugin     = " ", runtime    = " ",
      require    = "󰢱 ", source     = " ",
      start      = " ", task       = "✔ ",
    },
  },
})

-- ── Keymaps ───────────────────────────────────────────────────
local map = function(mode, lhs, rhs, desc)
  vim.keymap.set(mode, lhs, rhs, { silent = true, desc = desc })
end

map("n", "<C-h>", "<C-w>h",              "Move to left window")
map("n", "<C-j>", "<C-w>j",              "Move to lower window")
map("n", "<C-k>", "<C-w>k",              "Move to upper window")
map("n", "<C-l>", "<C-w>l",              "Move to right window")
map("n", "<S-l>", "<cmd>bnext<cr>",      "Next buffer")
map("n", "<S-h>", "<cmd>bprevious<cr>",  "Prev buffer")
map("n", "<leader>q",  "<cmd>bdelete<cr>",  "Close buffer")
map("n", "<leader>sv", "<cmd>vsplit<cr>",   "Vertical split")
map("n", "<leader>sh", "<cmd>split<cr>",    "Horizontal split")
map("v", "<", "<gv",                     "Indent left")
map("v", ">", ">gv",                     "Indent right")
map("v", "<A-j>", ":m '>+1<cr>gv=gv",   "Move line down")
map("v", "<A-k>", ":m '<-2<cr>gv=gv",   "Move line up")
map("n", "<leader>h", "<cmd>nohlsearch<cr>", "Clear highlight")
map("n", "<leader>w", "<cmd>w<cr>",      "Save")
map("n", "<leader>Q", "<cmd>qa<cr>",     "Quit all")
