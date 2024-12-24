<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use App\Enums\EmotionType;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('messages', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('message');
            $table->boolean('is_spam')->default(false);
            $table->boolean('is_real_spam')->default(false);
            $table->string('emotion')->default(EmotionType::NEUTRAL->value);
            $table->string('emotion_real')->default(EmotionType::NEUTRAL->value);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('messages');
    }
};
