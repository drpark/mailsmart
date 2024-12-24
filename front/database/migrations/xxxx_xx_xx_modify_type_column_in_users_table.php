<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;
use App\Enums\UserType;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            // On supprime d'abord la colonne existante si elle existe
            $table->dropColumn('type');
        });

        Schema::table('users', function (Blueprint $table) {
            // On la recrée comme string
            $table->string('type')->default(UserType::USER->value);
        });

        // Ajout de la contrainte via DB::statement
        DB::statement("ALTER TABLE users ADD CONSTRAINT check_user_type CHECK (type IN ('admin', 'user'))");
    }

    public function down(): void
    {
        if (DB::getDriverName() !== 'sqlite') {
            DB::statement('ALTER TABLE users DROP CONSTRAINT check_user_type');
        }

        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn('type');
        });
    }
};
