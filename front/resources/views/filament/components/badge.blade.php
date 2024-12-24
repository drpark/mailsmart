<div @class([
    'px-2 py-1 inline-flex items-center justify-center rounded-full text-xs font-medium',
    'bg-danger-100 text-danger-700' => $color === 'danger',
    'bg-success-100 text-success-700' => $color === 'success',
    'bg-primary-100 text-primary-700' => $color === 'primary',
])>
    {{ $label }}
</div>
