// Optional scaffold binding. The published dashboard uses no database.
declare namespace Cloudflare {
  interface Env {
    DB?: D1Database;
  }
}
