from typing import Annotated, List, Optional, Literal

from pydantic import BaseModel, Field, model_validator

class GameSettings(BaseModel):
    Language: Literal['ch','cz','en','fr','ge','hu','it','jp','kr','pl','po','sk','es','es-mx','tu','ru','ro','vi','in','th']
    SelectedMemberCategory: str
    QuickSlotsVisibility: str
    StaminaVisibility: str
    HealthVisibility: str
    HealthColor: str
    NotificationTransportType: str
    ConnectionType: str
    HighlightScope: str
    FieldOfView: int
    HeadBobbing: float
    AutoEmptyWorkingSet: bool
    SetAffinityToLogicalCores: bool
    EnableHideoutPreload: bool
    StreamerModeEnabled: bool
    BlockGroupInvites: bool
    ItemQuickUseMode: str
    PriorityWindowMode: str
    AutoVaultingMode: str
    ContinuousHealMode: str
    QuestItemNotificationMode: Optional[str] = Field(default=None)
    QuestItemSearchMode: Optional[str] = Field(default=None)
    WishlistNotificationsType: str
    AutoAddToWishlist: str
    MalfunctionVisability: bool
    TradingIntermediateScreen: bool
    RagfairLinesCount: int
    EnvironmentUiType: str
    TacticalInputMode: str

class SoundSettings(BaseModel):
    OverallVolume: int
    InterfaceVolume: int
    ChatVolume: int
    MusicVolume: int
    HideoutVolume: int
    MusicOnRaidEnd: bool
    VoipEnabled: bool
    VoipDevice: str
    VoiceChatVolume: Optional[int] = Field(le=100, ge=0, default=None)
    MicrophoneSensitivity: Optional[int] = Field(default=None)
    DenoiseAmount: Optional[str] = Field(default=None)

class PostFxSettings(BaseModel):
    EnablePostFx: bool
    Brightness: int = Field(description='亮度', ge=-100, le=100)
    Saturation: int = Field(description='Unknow')
    Colorfulness: int = Field(description='Unknow')
    Clarity: int = Field(description='清晰度', ge=-100, le=100)
    LumaSharpen: int = Field(description='光線銳化', ge=0, le=100)
    AdaptiveSharpen: int = Field(description='適應性銳化', ge=0, le=100)
    ColorFilterType: Literal['None', 'K506', 'Zabid', 'Cognac', 'Edwards', 'Cheese', 'LateGoose', 'Bread', 'Montreal', 'Feather', 'Jason', 'Fahrenheit', 'Owl', 'Chillwave', 'Albert', 'Bayswater', 'Atlanta', 'Felicity', 'Stefano', 'Boost', 'Emilia', 'Doze', 'Clifden', 'Blender', 'Tokyo', 'Walk', 'Olive', 'Hotshot'] = Field(description='顏色分級')
    Intensity: int = Field(description='顏色分級強度', ge=0, le=100)
    ColorBlindnessType: Literal['None', 'Tritanopia','Protanopia','Deuteranopia'] = Field(description='色盲模式')# Tritanopia:藍色盲, Protanopia:紅色盲, Deuteranopia:綠色盲
    ColorBlindnessIntensity: int = Field(description='色盲模式強度', ge=0, le=100)

# Graphics settings
class Resolution(BaseModel):
    Width: int
    Height: int

class AspectRatio(BaseModel):
    X: int
    Y: int

class StoredItem(BaseModel):
    Index: int
    FullScreenResolution: Resolution
    FullScreenAspectRatio: AspectRatio
    WindowResolution: Resolution
    WindowAspectRatio: AspectRatio

class DisplaySettings(BaseModel):
    Display: int
    FullScreenMode: int
    Resolution: Resolution
    AspectRatio: AspectRatio

class GraphicsSettings(BaseModel):
    Stored: List[StoredItem]
    DisplaySettings: DisplaySettings
    GraphicsQuality: Optional[str]
    ShadowsQuality: int
    TextureQuality: int
    CloudsQuality: str
    SDMode: Optional[str]
    VSync: bool
    LobbyFramerate: int
    GameFramerate: int
    DisableGameFramerateLimit: bool
    SuperSampling: str
    AnisotropicFiltering: str
    OverallVisibility: float
    LodBias: float
    MipStreamingBufferSize: int
    MipStreamingIOCount: int
    Ssao: str
    Sharpen: float
    SSR: str
    AntiAliasing: str
    NVidiaReflex: str
    HighQualityFog: bool
    GrassShadow: bool
    ChromaticAberrations: bool
    Noise: bool
    ZBlur: bool
    AreaLightsInstancing: Optional[bool] = Field(default=None)
    HighQualityColor: bool
    SdTarkovStreets: bool
    VolumetricLight: str|bool
    DLSSMode: str
    FSR2Mode: str
    FSR3Mode: str
    DLSSPreset: str
    InApplyDisplaySettingsProcess: bool
    DLSSEnabled: bool
    FSR2Enabled: bool
    FSR3Enabled: bool
    ShadowDistance: float
    SuperSamplingFactor: float
    MipStreaming: Optional[bool] = Field(default=None, deprecated=True)
    @model_validator(mode='after')
    def check_Upscaling_enabled(self)->'GraphicsSettings':
        if sum([self.DLSSEnabled, self.FSR2Enabled, self.FSR3Enabled]) >1:
            pass
        return self

# Control settings
class KeyCodeBinding(BaseModel):
    isAxis: Optional[bool] = None
    keyCode: List[str]
    axisName: Optional[str] = None
    positiveAxis: Optional[bool] = None
    sensitivity: Optional[float] = None

class AxisPair(BaseModel):
    positive: KeyCodeBinding
    negative: KeyCodeBinding

class AxisBinding(BaseModel):
    axisName: str
    pairs: List[AxisPair]

class Variant(BaseModel):
    isAxis: Optional[bool] = None
    keyCode: List[str]
    axisName: Optional[str] = None
    positiveAxis: Optional[bool] = None

class KeyBinding(BaseModel):
    keyName: str
    variants: Annotated[list[Variant], Field(min_length=2, max_length=2)]
    pressType: Literal['DoubleClick', 'Continuous', 'Press', 'Release']
    # Press:按下;DoubleClick:雙擊;Release:鬆開;Continuous:按住

class ControlSettings(BaseModel):
    InvertedXAxis: bool = Field(description='反轉 x 軸')
    InvertedYAxis: bool = Field(description='反轉 y 軸')
    MouseSensitivity: float
    MouseAimingSensitivity: float
    DoubleClickTimeout: float = Field(description='雙擊判斷間隔')
    OpticSensitivity: float
    axisBindings: List[AxisBinding]
    keyBindings: List[KeyBinding]