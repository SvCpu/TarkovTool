# Field
| 參數名稱 | 功能說明 | 簡單用法 |
| --- | --- | --- |
| default | 設定欄位的固定預設值，適合用在簡單型別或固定值。 | ``Field(default=0)`` |
| default_factory | 設定欄位的工廠函式，用來動態生成預設值，常用於可變型別（如 dict、list）。 | ``Field(default_factory=dict)`` |
| alias | 指定輸入資料或 JSON 中的 key 名稱，讓模型欄位可以對應不同的外部名稱。 | ``Field(alias="user_id")`` |
| title | 欄位的標題，主要用於文件生成或 API schema 描述。 | ``Field(title="使用者名稱")`` |
| description | 欄位的詳細描述，常用於 API 文件或 schema 說明。 | ``Field(description="必須是合法的 ``email")`` |
| gt | 限制數值必須大於指定值。 | ``Field(gt=0)`` |
| ge | 限制數值必須大於或等於指定值。 | ``Field(ge=0)`` |
| lt | 限制數值必須小於指定值。 | ``Field(lt=100)`` |
| le | 限制數值必須小於或等於指定值。 | ``Field(le=100)`` |
| min_length | 限制字串或集合的最小長度。 | ``Field(min_length=3)`` |
| max_length | 限制字串或集合的最大長度。 | ``Field(max_length=20)`` |
| pattern | 使用正則表達式驗證字串格式。 | ``Field(pattern=r"^[A-Za-z]+$")`` |
| strict | 啟用嚴格型別檢查，避免自動轉型。 | ``Field(strict=True)`` |
| const | 限制欄位值必須等於指定常數。 | ``Field(const=True)`` |
| multiple_of | 限制數值必須是某個數的倍數。 | ``Field(multiple_of=5)`` |
| examples | 提供範例值，主要用於文件生成或 API schema。 | ``Field(examples=["Alice", ``"Bob"])`` |
| deprecated | 標記欄位為已棄用，提示使用者不要再使用。 | ``Field(deprecated=True)`` |