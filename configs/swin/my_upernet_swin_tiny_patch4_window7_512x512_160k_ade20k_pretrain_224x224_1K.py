_base_ = [
    '../_base_/models/upernet_custom_swin.py', '../_base_/datasets/oct_hcms2018.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_epoch.py'
]
# checkpoint_file = 'https://download.openmmlab.com/mmsegmentation/v0.5/pretrain/swin/swin_tiny_patch4_window7_224_20220317-1cdeb081.pth'  # noqa
NUM_CLASSES = 9


model = dict(
    backbone=dict(
        # init_cfg=dict(type='Pretrained', checkpoint=checkpoint_file),
        embed_dims=96,
        depths=[2, 2, 6, 2],
        num_heads=[3, 6, 12, 24],
        window_size=7,
        patch_size=4,
        strides=(4, 2, 2, 2),
        qkv_bias=True,
        qk_scale=True,
        use_abs_pos_embed=False,
        drop_rate=0.,
        drop_path_rate=0.3,
        attn_drop_rate=0.2,
        patch_norm=True),
    decode_head=dict(in_channels=[96, 192, 384, 768], num_classes=NUM_CLASSES, channels=512, dropout_ratio=0.2,
                     # TODO 此处添加配置信息msc_module_cfg
                     # msc_module_cfg=[
                     #     dict(type='PPM', layer_idx=0), dict(type='PPM', layer_idx=1),
                     #     dict(type='PPM', layer_idx=2), dict(type='PPM', layer_idx=3)]
                     msc_module_cfg=[dict(type='PPM', layer_idx=3)]
                     # msc_module_cfg=[
                     #     dict(type='PPM', layer_idx=2), dict(type='PPM', layer_idx=3)]
                     # msc_module_cfg=[
                     #     dict(type='PPM', layer_idx=1), dict(type='PPM', layer_idx=2),
                     #     dict(type='PPM', layer_idx=3)]
                     ),
    auxiliary_head=dict(in_channels=384, dropout_ratio=0.1, num_classes=NUM_CLASSES))

# AdamW optimizer, no weight decay for position embedding & layer norm in backbone
optimizer = dict(
     _delete_=True,
     type='AdamW',
     lr=0.00006,
     betas=(0.9, 0.999),
     weight_decay=0.01,
     paramwise_cfg=dict(
         custom_keys={
             'absolute_pos_embed': dict(decay_mult=0.),
             'relative_position_bias_table': dict(decay_mult=0.),
             'norm': dict(decay_mult=0.),
             'head': dict(lr_mult=10.)
         }))
optim_wrapper = dict(
    type='AmpOptimWrapper',
    optimizer=dict(
        type='AdamW', lr=0.00006, betas=(0.9, 0.999), weight_decay=0.01))
param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=0.01,
        by_epoch=True,
        begin=0,
        end=2,
        convert_to_iter_based=True),
    dict(
        type='CosineAnnealingLR',
        # eta_min=1e-9,
        T_max=3,
        by_epoch=True,
        begin=2,
        end=5,
        convert_to_iter_based=True)
]

lr_config = dict(
    _delete_=True,
    policy='poly',
    warmup='linear',
    warmup_iters=1500,
    warmup_ratio=1e-6,
    power=1.0,
    min_lr=0.0,
    # by_epoch=True
)

# By default, models are trained on 8 GPUs with 2 images per GPU
# CUDA out of memory。 加载验证数据集时内存会爆掉， workers_per_gpu设置的小一些可避免这个问题
data = dict(samples_per_gpu=8,
            val_dataloader=dict(samples_per_gpu=8, workers_per_gpu=1, shuffle=False),
            test_dataloader=dict(samples_per_gpu=8, workers_per_gpu=1, shuffle=False))

